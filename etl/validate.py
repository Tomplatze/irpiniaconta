"""Validate bundled evidence and the actual PostgreSQL publication without writing data."""
import argparse
import hashlib
import json
from pathlib import PurePosixPath
import re

from etl.database import connect, require_current_schema
from etl.models import AdapterResult, Entity, Observation
from etl.pipeline import ROOT, replay_snapshot
from etl.publication_assets import DOCUMENT_PATHS, load_assets
from etl.quality import assess, validate_registry
from etl.sections import is_public_metric, read_snapshot, validate_publication


def validate_published_assets(database, codes: set[str], indicator_ids: set[str], source_ids: set[str]) -> dict:
    """Check current stored declarations against every current BYTEA download."""
    documents = dict(database.execute('SELECT key,document FROM atlas.publication_documents'))
    if set(documents) != set(DOCUMENT_PATHS):
        raise ValueError('Published collection-inventory, sections-map and editorial documents are required.')
    inventory = documents['collection-inventory']
    datasets = inventory.get('datasets', [])
    if (inventory.get('schema_version') != 1 or not datasets
            or len(datasets) != inventory.get('summary', {}).get('collected_dataset_families')
            or len({row['id'] for row in datasets}) != len(datasets)):
        raise ValueError('Published collection inventory is incomplete or inconsistent.')
    if {row['id'] for row in inventory.get('sources', [])} != source_ids:
        raise ValueError('Published collection inventory and source registry disagree.')
    map_codes = [row.get('code') for row in documents['sections-map'].get('features', [])]
    if len(map_codes) != 118 or set(map_codes) != codes:
        raise ValueError('Published display map and municipal registry disagree.')
    editorial_ids = [row.get('id') for row in documents['editorial'].get('indicators', [])]
    if not editorial_ids or len(set(editorial_ids)) != len(editorial_ids) or not set(editorial_ids) <= indicator_ids:
        raise ValueError('Published editorial selection contains missing or unknown indicators.')
    expected = {}
    for dataset in datasets:
        declarations = [(dataset['staging_file'], dataset['staging_sha256'], 'source-rows')]
        declarations.extend((row['path'], row['sha256'], 'metadata') for row in dataset.get('metadata_files', []))
        for name, checksum, kind in declarations:
            path = PurePosixPath(name)
            suffix = '.rows.jsonl.gz' if kind == 'source-rows' else '.json'
            if (str(path) != name or len(path.parts) != 3 or path.parts[:2] != ('data', 'collection')
                    or not re.fullmatch(r'[A-Za-z0-9_.-]+', path.name) or not path.name.endswith(suffix)
                    or not re.fullmatch(r'[a-f0-9]{64}', checksum)):
                raise ValueError(f'Published artifact declaration is invalid: {name}')
            if name in expected and expected[name] != (checksum, kind):
                raise ValueError(f'Conflicting published artifact declaration: {name}')
            expected[name] = checksum, kind
    actual = database.execute('SELECT path,payload,sha256,kind,octet_length(payload) FROM atlas.publication_artifacts').fetchall()
    if {row[0] for row in actual} != set(expected):
        raise ValueError('Published downloads do not match the current inventory allowlist.')
    for name, payload, checksum, kind, length in actual:
        if (expected[name] != (checksum, kind) or not length or len(payload) != length
                or hashlib.sha256(payload).hexdigest() != checksum):
            raise ValueError(f'Published artifact checksum, length or kind mismatch: {name}')
        if kind == 'metadata':
            json.loads(payload)
        elif not payload.startswith(b'\x1f\x8b'):
            raise ValueError(f'Published source download is not gzip: {name}')
    return {'documents': len(documents), 'verified_downloads': len(actual),
            'verified_download_bytes': sum(row[4] for row in actual)}


def validate_published(database, dataset_id: str | None = None) -> dict:
    """Reconstruct stored measurements and apply the same semantic rules as ingestion."""
    require_current_schema(database)
    municipalities = [dict(zip(['code','name','province_code','region_code'], row)) for row in database.execute(
        'SELECT code,name,province_code,region_code FROM atlas.municipalities')]
    codes = validate_registry(municipalities)
    selected_registry = dict(database.execute('SELECT code,name FROM sections.municipalities'))
    if {row['code']: row['name'] for row in municipalities} != selected_registry:
        raise ValueError('Published municipal registries disagree.')
    results = {}
    for identity, metadata, status, verified_at in database.execute('SELECT id,metadata,status,verified_at FROM atlas.datasets ORDER BY position'):
        if metadata.get('id') != identity or metadata.get('status') != status or metadata.get('verified_at') != verified_at:
            raise ValueError(f'Published dataset columns and metadata disagree: {identity}')
        results[identity] = AdapterResult(metadata)
    sources = dict(database.execute('SELECT id,metadata FROM atlas.source_registry'))
    if not sources or set(results) != {row.get('dataset_id') or identity for identity, row in sources.items()}:
        raise ValueError('Published core datasets do not match the source registry.')
    indicators = {}
    for identity, dataset, label, unit, definition in database.execute('SELECT id,dataset_id,label,unit,definition FROM atlas.indicators'):
        expected = next((row for row in results[dataset].metadata['indicators'] if row['id'] == identity), None)
        if not expected or (label, unit, definition) != (expected['label'], expected['unit'], expected['definition']):
            raise ValueError(f'Published indicator columns and metadata disagree: {identity}')
        indicators[identity] = dataset
    if set(indicators) != {row['id'] for result in results.values() for row in result.metadata['indicators']}:
        raise ValueError('Published indicator definitions are missing.')
    for row in database.execute('SELECT municipality_code,indicator_id,period,value,status FROM atlas.observations'):
        results[indicators[row[1]]].observations.append(Observation(*row))
    for dataset, source, code, title, kind, period, payload in database.execute(
            'SELECT dataset_id,source_id,municipality_code,title,kind,period,payload FROM atlas.entities'):
        results[dataset].entities.append(Entity(code, dataset, source, title, kind, payload, period))
    if dataset_id and dataset_id not in results:
        raise ValueError(f'Unknown published dataset: {dataset_id}')
    quality = [assess(result, codes) for identity, result in results.items() if not dataset_id or identity == dataset_id]

    categories = []
    for identity, metadata in database.execute('SELECT id,metadata FROM sections.categories ORDER BY position'):
        if metadata.get('id') != identity:
            raise ValueError(f'Published category columns and metadata disagree: {identity}')
        categories.append(metadata)
    metrics = {}
    for identity, category, metadata in database.execute('SELECT id,category,metadata FROM sections.metrics ORDER BY position'):
        if metadata.get('category') != category:
            raise ValueError(f'Published metric columns and metadata disagree: {identity}')
        metrics[identity] = {**metadata, 'cells': [], 'monthly': []}
    if not categories or not metrics:
        raise ValueError('Published selected metrics are empty.')
    for table, part in [('values_annual','cells'), ('values_monthly','monthly')]:
        for identity, code, period, value, status, weight in database.execute(
                f'SELECT metric,code,period,value,status,weight FROM sections.{table}'):
            metrics[identity][part].append({'code': code, 'period': period, 'value': value, 'status': status, 'weight': weight})
    for identity, metric in metrics.items():
        periods = sorted({row['period'] for row in metric['cells']})
        if (metric.get('id') != identity or not periods or not any(row['status'] == 'observed' for row in metric['cells'])
                or metric.get('periods') != periods or metric.get('latest_period') != periods[-1]
                or bool(metric.get('has_monthly')) != bool(metric['monthly'])):
            raise ValueError(f'Published metric periods, latest value or coverage disagree: {identity}')
        if any(not re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])', row['period']) or row['period'][:4] not in periods
               for row in metric['monthly']):
            raise ValueError(f'Published monthly and annual periods disagree: {identity}')
    for category in categories:
        category_metrics = {identity for identity, metric in metrics.items() if metric['category'] == category['id']}
        if category.get('primary') not in category_metrics or category.get('headline') not in category_metrics:
            raise ValueError(f'Published category selections are invalid: {category["id"]}')
    validate_publication({'municipalities': [{'code': code, 'name': name} for code, name in selected_registry.items()],
                          'metrics': list(metrics.values())})
    publications = database.execute('SELECT metadata FROM sections.publication').fetchall()
    if len(publications) != 1 or not publications[0][0].get('generated_at') or not isinstance(publications[0][0].get('lineage'), dict):
        raise ValueError('Selected publication provenance must contain exactly one record.')
    if database.execute("SELECT count(*) FROM pg_constraint WHERE connamespace IN ('atlas'::regnamespace,'sections'::regnamespace) AND NOT convalidated").fetchone()[0]:
        raise ValueError('PostgreSQL contains unvalidated publication constraints.')
    assets = validate_published_assets(database, codes, set(indicators), set(sources))
    return {'municipalities': len(codes), 'core_datasets': len(results), 'datasets_checked': len(quality),
            'ready_datasets': sum(row['status'] == 'ready' for row in quality),
            'blocked_datasets': sum(row['status'] == 'blocked' for row in quality),
            'core_indicators': len(indicators), 'core_observations': sum(len(row.observations) for row in results.values()),
            'core_observations_checked': sum(row['rows'] for row in quality),
            'core_entities': sum(len(row.entities) for row in results.values()), 'selected_metrics': sum(is_public_metric(metric) for metric in metrics.values()),
            'supporting_historical_series': sum(metric.get('presentation_role') == 'supporting_history' for metric in metrics.values()),
            'supporting_breakdown_series': sum(metric.get('presentation_role') == 'supporting_breakdown' for metric in metrics.values()),
            'stored_metric_definitions': len(metrics),
            'selected_annual_observations': sum(len(row['cells']) for row in metrics.values()),
            'selected_monthly_observations': sum(len(row['monthly']) for row in metrics.values()), **assets}


def main() -> None:
    """Report bundled and published counts separately; never mistake one for the other."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', help='Optional normalized dataset ID or central source ID.')
    arguments = parser.parse_args()
    municipalities, datasets, _ = replay_snapshot(ROOT / 'data/snapshot.json')
    bundled_dataset_count = len(datasets)
    bundled_observation_count = sum(len(row.observations) for row in datasets)
    codes = validate_registry(municipalities)
    selected = read_snapshot()
    dataset_id = arguments.dataset
    if dataset_id:
        source = next((row for row in json.loads((ROOT / 'config/sources.json').read_text())['sources'] if row['id'] == dataset_id), None)
        dataset_id = (source.get('dataset_id') or source['id']) if source else dataset_id
        datasets = [row for row in datasets if row.metadata['id'] == dataset_id]
    for result in datasets:
        assess(result, codes)
    if {row['code']: row['name'] for row in municipalities} != {row['code']: row['name'] for row in selected['municipalities']}:
        raise ValueError('Bundled municipal registries disagree.')
    documents, artifacts = load_assets()
    with connect() as database:
        database.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY')
        published = validate_published(database, dataset_id)
    print(json.dumps({'status': 'valid', 'database': 'PostgreSQL', 'published': published,
                      'bundled_snapshot': {'municipalities': len(codes), 'core_datasets': bundled_dataset_count,
                          'datasets_checked': len(datasets), 'core_observations': bundled_observation_count,
                          'core_observations_checked': sum(len(row.observations) for row in datasets),
                          'selected_metrics': sum(is_public_metric(metric) for metric in selected['metrics']),
                          'supporting_historical_series': sum(metric.get('presentation_role') == 'supporting_history' for metric in selected['metrics']),
                          'supporting_breakdown_series': sum(metric.get('presentation_role') == 'supporting_breakdown' for metric in selected['metrics']),
                          'stored_metric_definitions': len(selected['metrics']), 'documents': len(documents),
                          'verified_downloads': len(artifacts)}}, indent=2))


if __name__ == '__main__':
    main()
