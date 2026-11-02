"""Build the evidence-backed inventory from product imports and staged sources."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
import io
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build(root: Path = ROOT) -> dict[str, object]:
    """Generate all 81 scope states without calling a landing page an import."""
    config = json.loads((root / 'config/sources.json').read_text())
    collection = json.loads((root / 'config/collection.json').read_text())
    manifest = json.loads((root / 'data/collection/manifest.json').read_text())
    snapshot = json.loads((root / 'data/snapshot.json').read_text())
    results = {item['id']: item for item in manifest['jobs']}
    ready = {item['metadata']['source_id']: item for item in snapshot['datasets'] if item['metadata']['status'] == 'ready'}
    families: dict[str, list[dict[str, object]]] = {}
    for job in collection['jobs']:
        if results.get(job['id'], {}).get('status') == 'collected':
            families.setdefault(job.get('family', job['id']), []).append(job)
    datasets = []
    for family, jobs in families.items():
        acquired = [results[job['id']] for job in jobs]
        if jobs[0].get('paginated_total_count'):
            identifiers = [identifier for item in acquired for identifier in item['profile']['source_feature_ids']]
            if len(identifiers) != jobs[0]['paginated_total_count'] or len(set(identifiers)) != len(identifiers):
                raise ValueError('Incomplete or overlapping paginated source family: ' + family)
        codes = sorted({code for item in acquired for code in item['profile']['municipality_codes']})
        periods = sorted({period for item in acquired for period in item['profile']['periods']})
        tables: dict[str, list[str]] = {}
        for item in acquired:
            for table, detail in item['profile']['tables'].items():
                tables[table] = list(dict.fromkeys(tables.get(table, []) + detail['fields']))
        staging_path = root / 'data/collection' / f'{family}.rows.jsonl.gz'
        if len(jobs) > 1:
            temporary = staging_path.with_suffix('.pending.gz')
            with temporary.open('wb') as binary:
                with gzip.GzipFile(filename='', mode='wb', fileobj=binary, mtime=0) as compressed:
                    with io.TextIOWrapper(compressed, encoding='utf-8') as destination:
                        for item in acquired:
                            with gzip.open(root / item['profile']['staging_file'], 'rt', encoding='utf-8') as source:
                                for line in source:
                                    destination.write(line)
            temporary.replace(staging_path)
        else:
            staging_path = root / acquired[0]['profile']['staging_file']
        rows_by_period: Counter[str] = Counter()
        for item in acquired:
            rows_by_period.update(item['profile']['rows_by_period'])
        period_codes: dict[str, set[str]] = {}
        with gzip.open(staging_path, 'rt', encoding='utf-8') as source:
            for line in source:
                row = json.loads(line)
                period_codes.setdefault(row['period'], set()).update(row['municipality_codes'])
        metadata_files = []
        for item in acquired:
            for key in ['dimension_metadata_file', 'dictionary_file']:
                if item['profile'].get(key):
                    path = root / item['profile'][key]
                    metadata_files.append({'path': str(path.relative_to(root)), 'label': 'Dimensioni e definizioni' if key.startswith('dimension') else 'Dizionario delle variabili',
                                           'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        datasets.append({'id': family, 'title': jobs[0].get('title', family),
                         'publisher': jobs[0]['publisher'], 'period_semantics': jobs[0].get('period_semantics', 'Periodo dei dati dichiarato dalla fonte'),
                         'scope_ids': sorted({scope for job in jobs for scope in job['scope_ids']}),
                         'job_ids': [job['id'] for job in jobs], 'municipality_codes': codes,
                         'coverage': len(codes), 'record_count': sum(item['profile']['selected_rows'] for item in acquired),
                         'periods': periods, 'rows_by_period': dict(sorted(rows_by_period.items())), 'fields': tables,
                         'coverage_by_period': {period: len(values) for period, values in sorted(period_codes.items())},
                         'source_variables': sorted({variable for item in acquired for variable in item['profile'].get('source_variables', [])}),
                         'metadata_files': metadata_files,
                         'notes': jobs[0].get('notes', ''), 'license': jobs[0].get('license'),
                         'source_urls': list(dict.fromkeys(job['url'] for job in jobs)),
                         'format': jobs[0]['handler'], 'staging_file': str(staging_path.relative_to(root)),
                         'staging_sha256': hashlib.sha256(staging_path.read_bytes()).hexdigest(),
                         'publication_status': 'staging_only'})
    entries = []
    for scope in config['sources']:
        product = ready.get(scope['id'])
        available = [dataset for dataset in datasets if scope['id'] in dataset['scope_ids']]
        assessment = scope.get('collection', {})
        state = 'integrated' if product else assessment.get('relationship', 'collected') if available else 'not_collected'
        observed_codes = sorted({code for dataset in available for code in dataset['municipality_codes']} |
                                ({item['municipality_code'] for item in product['observations'] if item['value'] is not None} |
                                 {item['municipality_code'] for item in product.get('entities', []) if item['municipality_code']} if product else set()))
        periods = sorted({period for dataset in available for period in dataset['periods']} |
                         {item['period'] for item in product['observations']} if product else
                         {period for dataset in available for period in dataset['periods']})
        entries.append({'id': scope['id'], 'category_id': scope['category_id'], 'title': scope['title'],
                        'publisher': ' / '.join(dict.fromkeys(([product['metadata']['publisher']] if product else []) + [dataset['publisher'] for dataset in available])) or scope['publisher'],
                        'catalogue_publisher': scope['publisher'], 'landing_url': scope['landing_url'], 'status': state,
                        'product_integrated': product is not None, 'dataset_ids': [dataset['id'] for dataset in available],
                        'coverage': len(observed_codes), 'municipality_codes': observed_codes, 'periods': periods,
                        'assessment': assessment.get('note', ''), 'ui_summary': assessment.get('ui_summary', ''),
                        'blocker': assessment.get('blocker') if not available and not product else None,
                        'available_product_fields': [indicator['label'] for indicator in product['metadata']['indicators']] if product else [],
                        'product_metadata': product['metadata'] if product else None})
    categories = [{**category, 'scope_count': len([scope for scope in entries if scope['category_id'] == category['id']]),
                   'with_data_count': len([scope for scope in entries if scope['category_id'] == category['id'] and (scope['product_integrated'] or scope['dataset_ids'])])}
                  for category in config['categories']]
    inventory = {'schema_version': 1, 'generated_at': datetime.now(timezone.utc).isoformat(),
                 'publication_status': 'staging_only', 'municipality_count': 118,
                 'summary': {'scope_count': len(entries), 'product_integrated_count': len(ready),
                             'scope_with_data_count': sum(bool(entry['product_integrated'] or entry['dataset_ids']) for entry in entries),
                             'collected_dataset_families': len(datasets),
                             'collected_records': sum(dataset['record_count'] for dataset in datasets),
                             'status_counts': dict(Counter(entry['status'] for entry in entries))},
                 'categories': categories, 'sources': entries, 'datasets': datasets,
                 'failures': [{**item, 'resolved_by': next((job.get('resolved_by') for job in collection['jobs'] if job['id'] == item['id']), None)}
                              for item in manifest['jobs'] if item['status'] != 'collected']}
    temporary_inventory = root / 'data/collection/inventory.pending.json'
    temporary_inventory.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + '\n')
    temporary_inventory.replace(root / 'data/collection/inventory.json')
    write_report(inventory, root)
    return inventory


def write_report(inventory: dict[str, object], root: Path = ROOT):
    """Write an auditable report whose counts derive from actual staged records."""
    summary = inventory['summary']
    lines = ['# Data availability and collection evidence', '', f"Generated: {inventory['generated_at']}", '',
             f"All {summary['scope_count']} scope entries are assessed. {summary['scope_with_data_count']} have imported data or locally collected source records, including explicitly labelled partial/free alternatives. {summary['product_integrated_count']} are integrated into the legacy product-source store. {summary['collected_dataset_families']} staged dataset families contain {summary['collected_records']:,} source rows.", '',
             'The curated section publication is a separate layer over this collected evidence. Its selected metrics, graphical presentation and publication coverage are documented in [Sections](SECTIONS.md). Collection readiness does not imply that every field is published.', '',
             'This is a collection inventory, not a claim that every dataset is integrated, current, complete, or suitable for municipal comparisons. A scope entry can name a broad portal; the 81 entries are not 81 independent downloadable datasets.', '',
             '## Read and reproduce', '', '```sh', '.venv/bin/python -m etl.collect --offline', '.venv/bin/python -m etl.collection_report', '```', '',
             'Install optional geographic dependencies with `pip install -r requirements-collection.txt`. Omit `--offline` only for a deliberate manual re-acquisition. Use `--only JOB_ID` to inspect a source independently. Commands never update the product database or activate scheduling. Original bytes and request provenance live in `data/raw/collection`; reconciled original-field rows, dictionaries and metadata live in `data/collection`.', '',
             '## Interpretation rules', '',
             '- Coverage means at least one source record is associated with a municipality. Absence is not zero and does not demonstrate absence of a service, business, protected site or infrastructure.',
             '- Source periods, retrieval timestamps, estimates, forecasts, registers and reanalysis are distinct. There is no invented uniform current year.',
             '- All original variables are retained in staged rows. No automatic sums across sector hierarchies, financial totals, project phases or multiple geographic locations are published.',
             '- Original municipal codes are retained. Exact current-code/name crosswalks are explicit; historical municipal fusions are not silently aggregated.',
             '- Open-source application code does not change source conditions. Attribution and the known source terms are recorded; unknown terms do not prevent local technical collection.', '',
             '## Important verified limits', '',
             '- BDAP 2024 budget and indicator exports cover all 118 municipal authorities. The 2025 export covers 117; missing code 064105. Latest reporting year is not automatically the best common comparison year.',
             '- ISTAT ASIA local units/employees provide a free statistical alternative to a business-register extraction. Sector aggregates are not lists of companies or legal records.',
             '- Municipal agriculture was observed in the 2020 census. Organic crop records cover 114 municipalities and irrigation 116. Missing/suppressed combinations are retained, not reconstructed.',
             '- ISTAT projections are a median scenario, covering 17 Irpinia municipalities in the acquired export. They are not observed present-day population.',
             '- Open-Meteo ERA5-Land supplies 2025 daily reanalysis at one interior sample point for all 118 municipalities. History 2020–2025 was acquired for the first 10 only; wider parallel history requests received HTTP 429. Nearby municipalities may share a grid cell. These are not station observations or municipal averages.',
             '- Air/water measurements, hospitals, cultural places and mapped transport have limited observed spatial coverage. Hospital statistics in the acquired release refer to 2022, despite later file publication.',
             '- PNRR joins use CUP plus local project code. Project amounts must not be multiplied across locations. ANAC authority-location and contract-location relationships remain separate.',
             '- IdroGEO live detail contains population baselines from 2011/2021 and does not encode the hazard-map vintage in every response. Earthquake events are not a forecast or a risk ranking.',
             '- SIAT layers may be historic. Independent source counts detect truncation and error payloads, including HTTP-200 errors.', '',
             '- ISTAT monthly source rows include months 1–12 plus publisher-defined summary/adjustment rows 13 and 15. These are not 14 observed calendar months and must not be added blindly.',
             '- OpenCivitas source variable dictionaries, privacy and anomaly flags are retained. Fund calculation components are not observed cash receipts; nursery standard needs are not counts of available nursery places.', '',
             '## Category coverage', '', '| Category | Scope entries | Entries with data/explicit alternatives |', '|---|---:|---:|']
    for category in inventory['categories']:
        lines.append(f"| {category['label']} | {category['scope_count']} | {category['with_data_count']} |")
    lines.extend(['', '## All scope entries', '', '| ID | Original scope title | Collection state | Associated municipalities | Evidence and limits |', '|---|---|---|---:|---|'])
    for entry in inventory['sources']:
        note = entry['assessment'] or entry['blocker'] or 'Already imported; see source metadata and retained acquisition artifacts.'
        lines.append(f"| {entry['id']} | {entry['title']} | {entry['status']} | {entry['coverage']} | {note.replace('|', '/')} |")
    lines.extend(['', '## Staged source families and available fields', ''])
    for dataset in inventory['datasets']:
        lines.extend([f"### {dataset['id']}", '', f"Records: {dataset['record_count']:,}; associated municipalities: {dataset['coverage']}/118; periods: {', '.join(dataset['periods'])}.", '', dataset['notes'], '',
                      f"Staging file: `{dataset['staging_file']}`; SHA-256: `{dataset['staging_sha256']}`.", ''])
        for table, fields in dataset['fields'].items():
            lines.append(f"- `{table}` ({len(fields)} fields): " + ', '.join(f'`{field}`' for field in fields))
        if dataset['source_variables']:
            lines.append('- Original variable codes: ' + ', '.join(f'`{variable}`' for variable in dataset['source_variables']))
        lines.append('- Coverage by period: ' + ', '.join(f"{period}: {count}/118" for period, count in dataset['coverage_by_period'].items()))
        for metadata in dataset['metadata_files']:
            lines.append(f"- Original definitions: `{metadata['path']}`; SHA-256 `{metadata['sha256']}`.")
        lines.extend(['', f"Source: [{dataset['id']}]({dataset['source_urls'][0]})", ''])
    lines.extend(['## Failed or empty collections', ''])
    for failure in inventory['failures']:
        resolution = ' Resolved using: ' + ', '.join(failure['resolved_by']) + '.' if failure.get('resolved_by') else ''
        lines.append(f"- `{failure['id']}`: {failure.get('error', 'No matching records returned for this geography/period.')} Source artifacts remain inspectable.{resolution}")
    (root / 'docs').mkdir(exist_ok=True)
    (root / 'docs/DATA_AVAILABILITY.md').write_text('\n'.join(lines) + '\n')


if __name__ == '__main__':
    import fcntl
    with (ROOT / 'data/collection/collection.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit('Another collection run is active. Generate the inventory after it completes.')
        result = build()
    print(json.dumps(result['summary'], indent=2))
