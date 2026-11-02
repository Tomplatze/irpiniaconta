"""Manually acquire and inspect source records in a separate collection workspace.

This command never writes the product database or activates a scheduler. Failed
requests are reported independently and retain the previous valid staged output.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from etl.adapters.registry import parse_register
from etl.collection_profiles import Geography, profile
from etl.acquisition import Context
from etl.registry import load_collection, ordered_dependencies

ROOT = Path(__file__).resolve().parents[1]


def load_crosswalks(job: dict[str, object], geo: Geography, output: Path, raw_root: Path | None = None):
    """Load explicit source identifier links inside the guarded collection job."""
    raw_root = raw_root or ROOT / 'data/raw'
    # Station identifiers are loaded from the already verified source file.
    if job.get('station_crosswalk_file'):
        import csv
        with (raw_root / Path(str(job['station_crosswalk_file'])).relative_to('data/raw')).open(encoding='utf-8-sig', newline='') as handle:
            for row in csv.DictReader(handle):
                if row['Provincia'] == 'Avellino':
                    name = row['indirizzo'].split(' - ')[0]
                    codes = geo.resolve({'name': name}, {'key_rule': 'name', 'key_column': 'name'})
                    if codes:
                        for key in ['Codice Arpac', 'Codice Nazionale ', 'Codice Europeo']:
                            geo.stations[row[key]] = codes[0]
    if job.get('authority_crosswalk_job'):
        import gzip
        with gzip.open(output / f"{job['authority_crosswalk_job']}.rows.jsonl.gz", 'rt', encoding='utf-8') as handle:
            for line in handle:
                item = json.loads(line)
                fiscal = str(item['source']['CF Soggetto']).strip()
                code = item['municipality_codes'][0]
                if fiscal in geo.authorities and geo.authorities[fiscal] != code:
                    raise ValueError('Ambiguous BDAP authority fiscal-code crosswalk')
                geo.authorities[fiscal] = code
                identifier = str(item['source']['Codice BDAP']).strip()
                if identifier in geo.bdap_codes and geo.bdap_codes[identifier] != code:
                    raise ValueError('Ambiguous BDAP authority identifier crosswalk')
                geo.bdap_codes[identifier] = code
    if job.get('project_crosswalk_job'):
        import gzip
        with gzip.open(output / f"{job['project_crosswalk_job']}.rows.jsonl.gz", 'rt', encoding='utf-8') as handle:
            for line in handle:
                item = json.loads(line)
                key = (item['source']['CUP'], item['source']['Codice Locale Progetto'])
                geo.projects.setdefault(key, set()).update(item['municipality_codes'])
    if job.get('building_crosswalk_job'):
        import gzip
        with gzip.open(output / f"{job['building_crosswalk_job']}.rows.jsonl.gz", 'rt', encoding='utf-8') as handle:
            for line in handle:
                item = json.loads(line)
                geo.buildings[str(item['source']['CODICEEDIFICIO'])] = item['municipality_codes'][0]
    if job.get('civitas_crosswalk_file'):
        from openpyxl import load_workbook
        workbook = load_workbook(raw_root / Path(str(job['civitas_crosswalk_file'])).relative_to('data/raw'), read_only=True, data_only=True)
        mapping = {}
        columns = job.get('civitas_crosswalk', {})
        try:
            workbook.active.reset_dimensions()
            rows = workbook.active.iter_rows(values_only=True)
            headers = next(rows)
            for values in rows:
                row = dict(zip(headers, values))
                if columns.get('name_column'):
                    province = str(row[columns['province_column']]).strip().zfill(3)
                    codes = geo.resolve(row, {'key_rule': 'name', 'key_column': columns['name_column']}) if province == '064' else []
                    code = codes[0] if codes else None
                else:
                    code = str(row[columns.get('municipality_column', 'COMUNE_ISTAT_COD')]).zfill(6)
                type_column = columns.get('type_column', 'TIPOLOGIA_ENTE')
                if code in geo.codes and (type_column is None or row[type_column] == 'COMUNE'):
                    identifier = str(row['USERNAME'])
                    if identifier in mapping and mapping[identifier] != code:
                        raise ValueError('Ambiguous OpenCivitas entity crosswalk')
                    mapping[identifier] = code
        finally:
            workbook.close()
        if set(mapping.values()) != geo.codes or len(mapping) != 118:
            raise ValueError('OpenCivitas entity crosswalk does not cover all 118 municipalities')
        geo.civitas = mapping


def run(*, offline: bool, selected: set[str] | None = None, root: Path = ROOT, raw_root: Path | None = None) -> dict[str, object]:
    """Replay verified requests or download the explicitly configured sources."""
    config = load_collection(root)
    unknown = (selected or set()) - {job['id'] for job in config['jobs']}
    if unknown:
        raise ValueError('Unknown collection jobs: ' + ', '.join(sorted(unknown)))
    raw_root = raw_root or root / 'data/raw'
    municipalities = parse_register(raw_root / 'istat_registry_2026.xlsx')
    geo = Geography(municipalities, raw_root / 'istat_registry_2026.xlsx')
    output = root / 'data/collection'
    output.mkdir(parents=True, exist_ok=True)
    manifest_path = output / 'manifest.json'
    previous = json.loads(manifest_path.read_text()) if manifest_path.exists() else {'jobs': []}
    results = {item['id']: item for item in previous['jobs']}
    attempts = []
    failed_dependencies = set()
    for job in ordered_dependencies(config['jobs'], selected):
        if job.get('enabled') is False:
            continue
        attempted_at = datetime.now(timezone.utc).isoformat()
        staged_path = output / f"{job['id']}.rows.jsonl.gz"
        temporary = output / f"{job['id']}.pending.rows.jsonl.gz"
        context = Context(raw_root / Path(str(job.get('raw_dir', 'data/raw/collection'))).relative_to('data/raw'), offline=offline)
        try:
            if failed_dependencies.intersection(job.get('depends_on', [])):
                raise ValueError('A required collection job failed validation')
            source = context.fetch(str(job['url']), str(job['filename']), method=job.get('method', 'GET'), body=job.get('body'))
            for reference in job.get('reference_requests', []):
                context.fetch(reference['url'], reference['filename'])
            for supporting in job.get('supporting_requests', []):
                path = context.fetch(supporting['url'], supporting['filename'])
                payload = json.loads(path.read_text())
                if supporting.get('format') == 'sparql_count':
                    bindings = payload.get('results', {}).get('bindings', [])
                    count = int(bindings[0]['count']['value']) if len(bindings) == 1 else None
                else:
                    count = payload.get('count')
                if count is None or count != supporting.get('expected_count', job.get('expected_count')):
                    raise ValueError('Independent source count changed or returned an error')
            load_crosswalks(job, geo, output, raw_root)
            evidence = profile(source, job, geo, temporary, raw_root=raw_root)
            temporary.replace(staged_path)
            evidence['staging_file'] = str(staged_path.relative_to(root))
            # Additional field dictionaries and dimension metadata are immutable
            # evidence for the same staged acquisition.
            for key in ['dimension_metadata_file', 'dictionary_file']:
                if key in evidence:
                    old = Path(evidence[key])
                    new = output / old.name.replace('.pending.', '.')
                    old.replace(new)
                    evidence[key] = str(new.relative_to(root))
            evidence['staging_sha256'] = hashlib.sha256(staged_path.read_bytes()).hexdigest()
            result = {'id': job['id'], 'scope_ids': job['scope_ids'], 'status': 'collected' if evidence['selected_rows'] else 'empty',
                      'checked_at': attempted_at, 'artifacts': context.artifacts,
                      'profile': evidence, 'notes': job.get('notes', ''), 'license': job.get('license'),
                      'publication_status': 'staging_only'}
            results[job['id']] = result
            print(f"{job['id']}: {result['status']}; {evidence['selected_rows']} rows; {evidence['covered_municipalities']}/118 municipalities", flush=True)
        except Exception as error:
            failed_dependencies.add(job['id'])
            temporary.unlink(missing_ok=True)
            result = {'id': job['id'], 'scope_ids': job['scope_ids'], 'status': 'failed',
                      'checked_at': attempted_at, 'error': f'{type(error).__name__}: {error}',
                      'artifacts': context.artifacts, 'publication_status': 'staging_only'}
            if results.get(job['id'], {}).get('status') == 'collected':
                results[job['id']]['last_failed_attempt'] = result
            else:
                results[job['id']] = result
            print(f"{job['id']}: FAILED: {result['error']}", flush=True)
        attempts.append(result)
        partial = {'attempts': attempts, 'schema_version': 1, 'checked_at': attempted_at, 'municipality_count': len(municipalities),
                   'publication_status': 'staging_only', 'jobs': list(results.values())}
        temporary_manifest = output / 'manifest.pending.json'
        temporary_manifest.write_text(json.dumps(partial, ensure_ascii=False, indent=2) + '\n')
        temporary_manifest.replace(manifest_path)
    return {'attempts': attempts, 'jobs': list(results.values())}


def main():
    """Expose a manual command with optional request-preserving offline replay."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offline', action='store_true', help='Require stored bytes and matching request provenance')
    parser.add_argument('--only', nargs='+', help='Explicit collection job identifiers')
    args = parser.parse_args()
    import fcntl
    lock_path = ROOT / 'data/collection/collection.lock'
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            parser.exit(2, 'Another collection run is active. Retry after it completes.\n')
        result = run(offline=args.offline, selected=set(args.only) if args.only else None)
    config = json.loads((ROOT / 'config/collection.json').read_text())
    active_ids = {job['id'] for job in config['jobs'] if job.get('enabled') is not False}
    failed = [item for item in result['attempts'] if item['status'] in {'failed', 'empty'} and item['id'] in active_ids and (not args.only or item['id'] in args.only)]
    raise SystemExit(1 if failed else 0)


if __name__ == '__main__':
    main()
