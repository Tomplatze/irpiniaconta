"""Plan, prepare and publish independent source updates without involving Nuxt."""
from __future__ import annotations

import argparse
from importlib.util import find_spec
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import uuid

from etl import collect, collection_report, refresh, sections
from etl.database import semantic_checksum
from etl.publication import baseline, load_prepared, publish_prepared
from etl.registry import load_collection, load_scope, ordered_dependencies
from etl.workspaces import (configuration_hash, create_workspace, file_hash, promote_files,
                            publication_files, publication_files_lock, run_path, save_report)

ROOT = Path(__file__).resolve().parents[1]


def plan(root: Path = ROOT, *, sources: set[str] | None = None, due: bool = False) -> dict:
    """Resolve source/job dependencies without network access or a database connection."""
    scope = load_scope(root)
    collection = load_collection(root)
    chosen = ordered_dependencies(scope['sources'], sources)
    previous = {}
    if due and (root / 'data/snapshot.json').exists():
        _, results, _ = refresh.replay_snapshot(root / 'data/snapshot.json')
        previous = {result.metadata['source_id']: result for result in results}
    active = {source['id'] for source in chosen if source.get('enabled', True) and
              (not due or refresh.due_source(source, previous.get(source['id']),
                                            timezone_name=scope['monthly_check']['timezone']))}
    # Dependencies follow any due dependent, even if their own cadence is longer.
    active = {source['id'] for source in ordered_dependencies(scope['sources'], active)}
    active = {source['id'] for source in scope['sources'] if source['id'] in active and source.get('enabled', True)}
    selected_jobs = {job['id'] for job in collection['jobs'] if job.get('enabled', True) and
                     any(identity in active for identity in job['scope_ids'])}
    jobs = [job['id'] for job in ordered_dependencies(collection['jobs'], selected_jobs) if job.get('enabled', True)]
    return {'sources': [source['id'] for source in ordered_dependencies(scope['sources'], active)],
            'jobs': jobs, 'configuration_sha256': configuration_hash(root)}


def prepare(root: Path = ROOT, *, sources: set[str] | None = None, offline: bool = False,
            due: bool = False, rebuild: bool = False) -> dict:
    """Build a complete candidate in isolation, preserving the live publication on failure."""
    selected = plan(root, sources=sources, due=due)
    if not rebuild and not selected['sources']:
        return {'status': 'unchanged', 'reason': 'No enabled sources are due', 'plan': selected}
    geographic = {'boundaries', 'geojson', 'weather', 'natura', 'osm', 'events', 'esri_lines'}
    jobs = load_collection(root)['jobs']
    if not rebuild and any(job['id'] in selected['jobs'] and job['handler'] in geographic for job in jobs):
        if any(find_spec(module) is None for module in ['shapely', 'pyproj', 'shapefile']):
            raise ValueError('Selected geographic sources require pip install -r requirements-collection.txt')
    expected_revision = baseline(root)
    identity = uuid.uuid4().hex
    directory = run_path(root, identity)
    directory.mkdir(parents=True)
    report = {'run_id': identity, 'status': 'preparing', 'started_at': datetime.now(timezone.utc).isoformat(),
              'plan': selected, 'expected_revision': expected_revision, 'offline': offline, 'rebuild': rebuild}
    save_report(directory / 'run.json', report)
    try:
        workspace = create_workspace(root, directory)
        if not rebuild:
            municipalities, datasets, core_report = refresh.prepare(
                offline=offline, source_ids=selected['sources'], probe=False,
                root=workspace, raw_dir=root / 'data/raw')
            report['source_attempts'] = core_report['attempts']
            retained_ready = {dataset.metadata['source_id'] for dataset in datasets if dataset.metadata['status'] == 'ready'}
            failed = [attempt for attempt in core_report['attempts'] if attempt.get('error') or
                      (attempt['status'] == 'blocked' and attempt['source_id'] in retained_ready)]
            if failed:
                raise ValueError('Core acquisition/validation failed: ' + ', '.join(item['source_id'] for item in failed))
            refresh.write_snapshot(municipalities, datasets, core_report, workspace)
            if selected['jobs']:
                collected = collect.run(offline=offline, selected=set(selected['jobs']), root=workspace,
                                        raw_root=root / 'data/raw')
                report['collection_attempts'] = collected['attempts']
                failed = [attempt for attempt in collected['attempts'] if attempt['status'] != 'collected']
                if failed:
                    raise ValueError('Collection acquisition/validation failed: ' + ', '.join(item['id'] for item in failed))
            if not (workspace / 'data/collection/manifest.json').exists():
                (workspace / 'data/collection/manifest.json').write_text('{"jobs":[]}\n')
            collection_report.build(workspace)
        document = sections.build(workspace)
        sections.ensure_map(workspace)
        payload = json.dumps(document, ensure_ascii=False, separators=(',', ':')).encode()
        (workspace / 'data/sections.snapshot.json').write_bytes(payload)
        (workspace / 'data/sections.snapshot.sha256').write_text(
            file_hash(workspace / 'data/sections.snapshot.json') + '  sections.snapshot.json\n')
        prepared = load_prepared(workspace)
        report['summary'] = {'municipalities': len(prepared.municipalities), 'datasets': len(prepared.datasets),
                             'stored_metrics': len(prepared.selected['metrics']), 'artifacts': len(prepared.assets[1])}
        report['files'] = publication_files(workspace)
        report['checksum'] = semantic_checksum(report['files'])
        if configuration_hash(root) != selected['configuration_sha256']:
            raise ValueError('Configuration changed during preparation; prepare a new run')
        report['status'] = 'prepared'
    except Exception as error:
        report['status'] = 'failed'
        report['error'] = f'{type(error).__name__}: {error}'
        raise
    finally:
        report['prepared_at'] = datetime.now(timezone.utc).isoformat()
        save_report(directory / 'run.json', report)
    return report


def publish(root: Path, identity: str) -> dict:
    """Commit a validated candidate and recover filesystem promotion after interruption."""
    directory = run_path(root, identity)
    report_path = directory / 'run.json'
    report = json.loads(report_path.read_text())
    if report['status'] == 'published':
        return report
    if report['status'] not in {'prepared', 'database_committed'}:
        raise ValueError('Only a successfully prepared run can be published')
    if configuration_hash(root) != report['plan']['configuration_sha256']:
        raise ValueError('Configuration changed after preparation; prepare a new run')
    workspace = directory / 'workspace'
    if publication_files(workspace) != report['files']:
        raise ValueError('Prepared files changed after validation; prepare a new run')
    prepared = load_prepared(workspace)
    try:
        result = publish_prepared(prepared, identity=identity, checksum=report['checksum'],
                                  expected_revision=report['expected_revision'])
        report['status'] = 'database_committed'
        report['database'] = result
        save_report(report_path, report)
        promote_files(workspace, root, report['files'])
        report['status'] = 'published'
        report['completed_at'] = datetime.now(timezone.utc).isoformat()
        report.pop('publication_error', None)
        save_report(report_path, report)
        shutil.rmtree(workspace)
        return report
    except Exception as error:
        report['publication_error'] = f'{type(error).__name__}: {error}'
        save_report(report_path, report)
        raise


def main() -> None:
    """Expose complete updates, preparation-only runs, plans and explicit publication retries."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['plan', 'prepare', 'update', 'publish'])
    parser.add_argument('--sources', help='Comma-separated central source IDs, including their dependencies')
    parser.add_argument('--offline', action='store_true', help='Replay verified raw acquisitions without network access')
    parser.add_argument('--due', action='store_true', help='Select sources due under the central refresh schedule')
    parser.add_argument('--rebuild', action='store_true', help='Rebuild existing staged evidence without acquisitions')
    parser.add_argument('--run', help='Prepared run identifier to publish or recover')
    arguments = parser.parse_args()
    sources = set(arguments.sources.split(',')) if arguments.sources else None
    try:
        if arguments.operation == 'plan':
            result = plan(sources=sources, due=arguments.due)
        else:
            with publication_files_lock(ROOT):
                if arguments.operation == 'publish':
                    if not arguments.run:
                        raise ValueError('--run is required for publication')
                    result = publish(ROOT, arguments.run)
                else:
                    if arguments.rebuild and (sources is not None or arguments.due):
                        raise ValueError('--rebuild uses all staged evidence; omit --sources and --due')
                    result = prepare(sources=sources, offline=arguments.offline, due=arguments.due,
                                     rebuild=arguments.rebuild)
                    if arguments.operation == 'update' and result['status'] == 'prepared':
                        result = publish(ROOT, result['run_id'])
    except (ValueError, RuntimeError, OSError, KeyError) as error:
        parser.exit(1, f'Data workflow failed: {error}\nSee .local/runs/*/run.json for the retained attempt.\n')
    # Detailed provenance stays in the local report; terminal output remains readable.
    print(json.dumps({key: value for key, value in result.items()
                      if key not in {'files', 'source_attempts', 'collection_attempts'}}, indent=2))


if __name__ == '__main__':
    main()
