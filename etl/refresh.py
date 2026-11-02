"""Central refresh coordinator: discovery, quarantine, history and last-valid publication."""
import argparse
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import asdict
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor,as_completed
import fcntl
import hashlib
import importlib
import inspect
import json
import os
from pathlib import Path
import uuid
from zoneinfo import ZoneInfo

from etl.acquisition import Context
from etl.models import AdapterResult
from etl.pipeline import ROOT,replay_snapshot,write_database,utc_now
from etl.quality import assess,validate_registry
from etl.registry import load_scope, ordered_dependencies


@contextmanager
def exclusive_refresh():
    """Prevent overlapping manual, scheduled and container refresh processes."""
    path=ROOT/'data/refresh.lock'
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a') as stream:
        try:fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise RuntimeError('A refresh is already running') from None
        try:yield
        finally:fcntl.flock(stream,fcntl.LOCK_UN)


def merge_valid(previous:AdapterResult|None,current:AdapterResult) -> AdapterResult:
    """Replace revised cells in the acquired periods and preserve older published history."""
    if previous is None:return current
    if current.metadata['status']=='blocked' and previous.metadata['status']=='ready':
        preserved=deepcopy(previous)
        preserved.metadata['last_attempt']=current.metadata['last_attempt']
        preserved.metadata['stale']=True
        return preserved
    if current.metadata['status']=='ready':
        allowed={i['id'] for i in current.metadata['indicators']}
        cells={(o.municipality_code,o.indicator_id,o.period):o for o in previous.observations if o.indicator_id in allowed}
        cells.update({(o.municipality_code,o.indicator_id,o.period):o for o in current.observations})
        current.observations=list(cells.values())
        current.metadata['stale']=False
    return current


def due_source(source:dict[str,object],previous:AdapterResult|None,now:datetime|None=None, timezone_name:str|None=None) -> bool:
    """Monthly means calendar-month change; other cadences use elapsed days."""
    attempt=(previous.metadata.get('last_attempt') or {}) if previous else {}
    timestamp=attempt.get('at')
    if not timestamp:return True
    zone=ZoneInfo(timezone_name or load_scope()['monthly_check']['timezone'])
    checked=datetime.fromisoformat(timestamp).astimezone(zone)
    now=(now or datetime.now(timezone.utc)).astimezone(zone)
    if source['cadence_days']==30:return (checked.year,checked.month)!=(now.year,now.month)
    return (now-checked).days>=source['cadence_days']


def pending_result(source:dict[str,object]) -> AdapterResult:
    """Keep unimplemented/restricted scope items explicit with zero fabricated measurements."""
    return AdapterResult({'id':source['id'],'name':source['title'],'publisher':source['publisher'],
      'landing_url':source['landing_url'],'download_url':None,'license':None,'license_url':None,
      'format':'Not validated','geography':source['geography'],'period':'unavailable','status':'blocked',
      'blocker':source['blocker'],'notes':'Registered scope item. A landing-page check is not dataset, licence or municipal-coverage verification.',
      'indicators':[],'artifacts':[],'verified_at':''})


def run_adapter(source,context,municipalities,school_links):
    """Bind declared adapter inputs while keeping source orchestration outside presentation."""
    module=importlib.import_module('etl.adapters.'+source['adapter'])
    available={'context':context,'codes':validate_registry(municipalities),'municipalities':municipalities,
               'adapter':source['dataset_id'],'school_links':school_links,'options':source['options']}
    signature=inspect.signature(module.run)
    return module.run(**{name:available[name] for name in signature.parameters})


def content_digest(result:AdapterResult) -> str:
    """Compare substantive data while ignoring acquisition timestamps of current-state snapshots."""
    snapshot=result.metadata.get('temporal_semantics')=='current_snapshot'
    rows=result.observations
    if snapshot:
        latest={}
        for row in rows:
            key=(row.municipality_code,row.indicator_id)
            if key not in latest or row.period>latest[key].period:latest[key]=row
        rows=list(latest.values())
    cells=sorted((row.municipality_code,row.indicator_id,'' if snapshot else row.period,row.value,row.status) for row in rows)
    records=sorted((row.source_id,row.municipality_code or '',row.title,row.payload) for row in result.entities)
    return hashlib.sha256(json.dumps({'cells':cells,'entities':records},sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def probe_landing(source,context,cache):
    """Record actual HTTP reachability once per URL; never upgrade readiness based on it."""
    url=source['landing_url']
    if url not in cache:
        try:
            path=context.fetch(url,'landing_'+hashlib.sha256(url.encode()).hexdigest()[:20]+'.html')
            cache[url]={'status':'reachable','artifact':context.artifacts[-1],'at':utc_now()}
        except Exception as error:
            cache[url]={'status':'failed','error':f'{type(error).__name__}: {error}','at':utc_now()}
    return cache[url]


def write_snapshot(municipalities, results, report, root: Path = ROOT) -> None:
    """Archive a prepared core publication without opening a database connection."""
    content = {'schema_version': 2, 'municipalities': municipalities,
               'datasets': [{'metadata': result.metadata,
                             'observations': [asdict(row) for row in result.observations],
                             'entities': [asdict(row) for row in result.entities]} for result in results],
               'report': report}
    payload = (json.dumps(content, ensure_ascii=False, indent=2) + '\n').encode()
    archive = root / 'data/history' / report['run_id']
    archive.mkdir(parents=True)
    (archive / 'snapshot.json').write_bytes(payload)
    (archive / 'snapshot.sha256').write_text(hashlib.sha256(payload).hexdigest() + '\n')
    (archive / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    for destination, data in [
        (root / 'data/snapshot.json', payload),
        (root / 'data/snapshot.sha256', (hashlib.sha256(payload).hexdigest() + '\n').encode()),
        (root / 'data/verification.json', (json.dumps(report, indent=2) + '\n').encode()),
    ]:
        temporary = destination.with_name(destination.name + '.tmp')
        temporary.write_bytes(data)
        os.replace(temporary, destination)


def prepare(offline=False, due=False, source_ids=None, probe=True, *, root: Path | None = None,
            raw_dir: Path | None = None):
    """Acquire and normalize core sources; do not publish files or database records."""
    root = root or ROOT
    scope=load_scope(root)
    chosen=ordered_dependencies(scope['sources'], set(source_ids) if source_ids is not None else None)
    selected={source['id'] for source in chosen}
    timezone_name=scope['monthly_check']['timezone']
    if selected-{s['id'] for s in scope['sources']}:raise ValueError('Unknown requested source ID')
    snapshot=root/'data/snapshot.json'
    previous={};old_report={}
    if snapshot.exists():
        municipalities,old_results,old_report=replay_snapshot(snapshot)
        previous={r.metadata['id']:r for r in old_results}
    started=utc_now();context=Context(raw_dir or root/'data/raw',offline)
    registry=importlib.import_module('etl.adapters.registry').run(context)
    municipalities=registry.municipalities;codes=validate_registry(municipalities)
    results=[];attempts=[];landing_cache={};school_links={};changes=[]
    active_sources=[source for source in scope['sources'] if source.get('enabled', True) and source['id'] in selected and
                    (not due or due_source(source,previous.get(source['dataset_id'] or source['id']),timezone_name=timezone_name))]
    if probe:
        unique={source['landing_url']:source for source in active_sources}
        def inspect_page(source):
            worker=Context(context.raw_dir,offline)
            check=probe_landing(source,worker,{})
            return source['landing_url'],check,worker.artifacts
        with ThreadPoolExecutor(max_workers=4) as pool:
            for future in as_completed([pool.submit(inspect_page,source) for source in unique.values()]):
                url,check,artifacts=future.result();landing_cache[url]=check;context.artifacts.extend(artifacts)
    # School records are acquired before provincial institute joins, regardless of catalogue display order.
    ordered=ordered_dependencies(scope['sources'])
    failed_dependencies=set()
    for source in ordered:
        dataset_id=source['dataset_id'] or source['id'];prior=previous.get(dataset_id)
        active=source.get('enabled', True) and source['id'] in selected and (not due or due_source(source,prior,timezone_name=timezone_name))
        if not active:
            result=prior or pending_result(source)
        else:
            first=len(context.artifacts)
            adapter_error=None
            try:
                if failed_dependencies.intersection(source.get('depends_on', [])):
                    raise RuntimeError('A required source failed validation')
                if source['adapter']:
                    result=run_adapter(source,context,municipalities,school_links)
                    assess(result,codes)
                else:result=pending_result(source)
            except Exception as error:
                adapter_error=f'{type(error).__name__}: {error}'
                result=AdapterResult({**(prior.metadata if prior else pending_result(source).metadata),
                    'id':dataset_id,'status':'blocked','blocker':f'{type(error).__name__}: {error}'})
            check=landing_cache.get(source['landing_url'])
            attempt={'at':utc_now(),'status':result.metadata['status'],'blocker':result.metadata.get('blocker'),
                     'artifacts':context.artifacts[first:],'landing_check':check,'error':adapter_error}
            result.metadata={**result.metadata,'source_id':source['id'],'category_id':source['category_id'],
              'verified_at':attempt['at'],'artifacts':context.artifacts[first:],'last_attempt':attempt,
              'update_policy':source['update_policy'],'cadence_days':source['cadence_days'],
              'temporal_semantics':source['temporal_semantics']}
            failed=result.metadata['status']=='blocked'
            if failed:failed_dependencies.add(source['id'])
            if prior:
                prior.metadata['temporal_semantics']=source['temporal_semantics']
            result=merge_valid(prior,result)
            if not failed and result.metadata['status']=='ready' and (prior is None or prior.metadata['status']!='ready' or content_digest(prior)!=content_digest(result)):
                changes.append({'source_id':source['id'],'type':'data_changed'})
            if prior and prior.metadata['status']=='ready' and failed and not prior.metadata.get('stale'):
                changes.append({'source_id':source['id'],'type':'new_update_failure','blocker':attempt['blocker']})
            if prior and prior.metadata.get('stale') and not failed:
                changes.append({'source_id':source['id'],'type':'update_recovered'})
            attempts.append({'source_id':source['id'],**attempt})
            print(f"{source['id']}: {result.metadata['status']} / {len(result.observations)} cells / {len(result.entities)} entities",flush=True)
        result.metadata={**result.metadata,'source_id':source['id'],'category_id':source['category_id'],
                         'temporal_semantics':source['temporal_semantics']}
        if source['adapter']=='mim_schools':
            for entity in result.entities:
                institution=str(entity.payload.get('CODICEISTITUTORIFERIMENTO',''))
                if institution==entity.payload.get('CODICESCUOLA'):school_links[institution]=entity.municipality_code
            # Institution headquarters must be an original school/institute record; pupil sites are not substituted.
        results.append(result)
    results.sort(key=lambda r:next(i for i,s in enumerate(scope['sources']) if s['id']==r.metadata.get('source_id',r.metadata['id'])))
    quality=[assess(r,codes) for r in results]
    report={'run_id':str(uuid.uuid4()),'started_at':started,'completed_at':utc_now(),'mode':'offline-raw' if offline else 'live',
            'municipality_count':len(municipalities),'registry_metadata':registry.metadata,'artifacts':context.artifacts,
            'quality':quality,'attempts':attempts,'source_checks':landing_cache,
            'scope_count':len(scope['sources']),'previous_run_id':old_report.get('run_id'),'changes':changes}
    return municipalities, results, report


def execute(offline=False, due=False, source_ids=None, probe=True):
    """Retain the explicit core-only command for adapter maintenance."""
    with exclusive_refresh():
        municipalities, results, report = prepare(offline, due, source_ids, probe)
        write_database(municipalities, results, report)
        write_snapshot(municipalities, results, report)
        return report


def main():
    """Expose one local entry point for manual and monthly execution."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offline',action='store_true');parser.add_argument('--due',action='store_true')
    parser.add_argument('--sources',help='Comma-separated catalogue IDs; preserve other published sources')
    parser.add_argument('--skip-probes',action='store_true',help='Skip landing checks during targeted development replay')
    args=parser.parse_args();report=execute(args.offline,args.due,args.sources.split(',') if args.sources else None,not args.skip_probes)
    print(json.dumps({'run_id':report['run_id'],'attempted_sources':len(report['attempts']),
                      'ready_sources':sum(q['status']=='ready' for q in report['quality']),
                      'blocked_sources':sum(q['status']=='blocked' for q in report['quality']),'changes':report['changes']},indent=2))


if __name__=='__main__':main()
