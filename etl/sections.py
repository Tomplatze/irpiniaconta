"""Build an atomic public-metric store from verified staging, independently of collection."""
from __future__ import annotations
import argparse
from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import fcntl
import json
import os
from pathlib import Path

from etl import section_normalization as normalize

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / 'data/sections.snapshot.json'


def is_public_metric(metric: dict) -> bool:
    """Keep internal historical companions out of public indicator counts and category choices."""
    role = metric.get('presentation_role', 'public')
    if role not in {'public', 'supporting_history', 'supporting_breakdown'}:
        raise ValueError(f"Unknown presentation role: {role}")
    return role == 'public'


def core_cells(snapshot: dict, recipe: dict) -> tuple[list[dict], list[dict], str]:
    """Retain previously verified values and their published source evidence unchanged."""
    dataset = next((dataset for dataset in snapshot['datasets'] if any(metric['id'] == recipe['indicator'] for metric in dataset['metadata']['indicators'])), None)
    if dataset is None:
        raise ValueError(f"Core indicator is not available in the prepared sources: {recipe['indicator']}")
    metric = next(metric for metric in dataset['metadata']['indicators'] if metric['id'] == recipe['indicator'])
    weights = {(row['municipality_code'], row['period']): row['value'] for result in snapshot['datasets'] for row in result['observations']
               if row['indicator_id'] == recipe.get('weight_indicator') and row['status'] == 'observed'}
    cells = [normalize.cell(row['municipality_code'], row['period'], row['value'], row['status'], weights.get((row['municipality_code'], row['period'])))
             for row in dataset['observations'] if row['indicator_id'] == recipe['indicator']]
    metadata = dataset['metadata']
    sources = [{'id': metadata['id'], 'title': metadata['name'], 'publisher': metadata['publisher'], 'url': metadata['landing_url'],
                'verified_at': metadata['verified_at'], 'license': metadata.get('license'), 'artifacts': metadata.get('artifacts', [])}]
    return cells, sources, metric['unit']


def build(root: Path = ROOT) -> dict:
    """Apply authored transformations only; fail the entire publication on invalid source shape."""
    configuration = json.loads((root / 'config/sections.json').read_text())
    snapshot = json.loads((root / 'data/snapshot.json').read_text())
    inventory = json.loads((root / 'data/collection/inventory.json').read_text())
    source_map = {dataset['id']: dataset for dataset in inventory['datasets']}
    categories = json.loads((root / 'config/sources.json').read_text())['categories']
    category_names = {row['id']: row['label'] for row in categories}
    registry = {row['code'] for row in snapshot['municipalities']}
    for category in configuration['categories']:
        selected = {metric['id'] for metric in configuration['metrics'] if metric['category'] == category['id'] and is_public_metric(metric)}
        if category['primary'] not in selected or category['headline'] not in selected:
            raise ValueError(f"Invalid category metric selection: {category['id']}")
    handlers = {'filtered': normalize.filtered, 'distinct': normalize.distinct, 'tourism': normalize.tourism,
                'foreign_residents': normalize.foreign_residents,
                'waste': normalize.waste, 'weather': normalize.weather}
    metrics = []
    for definition in configuration['metrics']:
        recipe = definition['recipe']; handler = recipe['handler']; extras = {}
        if handler == 'core':
            cells, sources, unit = core_cells(snapshot, recipe)
            unit = definition['unit'] or unit
        else:
            datasets = [source_map[id] for id in recipe['sources']]
            cells, extras = handlers[handler](root, datasets, recipe)
            sources = [{'id': dataset['id'], 'title': dataset['title'], 'publisher': dataset['publisher'], 'url': dataset['source_urls'][0],
                        'license': dataset['license'], 'staging_sha256': dataset['staging_sha256'], 'staging_file': dataset['staging_file'],
                        'metadata_files': dataset['metadata_files'], 'verified_at': inventory['generated_at']} for dataset in datasets]
            unit = definition['unit']
        if not cells or not any(row['status'] == 'observed' for row in cells):
            raise ValueError(f"Selected metric has no validated observations: {definition['id']}")
        validate_cells(cells, registry)
        if extras.get('monthly'):
            validate_cells(extras['monthly'], registry)
        periods = sorted({row['period'] for row in cells})
        metrics.append({**definition, 'unit': unit, 'sources': sources, 'periods': periods,
                        'latest_period': periods[-1], 'cells': cells, **extras})
        print(f"Validated {definition['id']}: {len(cells)} cells / {len(periods)} periods", flush=True)
    return {'schema_version': 1, 'generated_at': datetime.now(timezone.utc).isoformat(), 'municipalities': snapshot['municipalities'],
            'categories': [{**row, 'label': category_names[row['id']]} for row in configuration['categories']], 'metrics': metrics,
            'lineage': {'product_snapshot_sha256': hashlib.sha256((root / 'data/snapshot.json').read_bytes()).hexdigest(),
                        'collection_inventory_sha256': hashlib.sha256((root / 'data/collection/inventory.json').read_bytes()).hexdigest(),
                        'configuration_sha256': hashlib.sha256((root / 'config/sections.json').read_bytes()).hexdigest()}}


def validate_cells(cells: list[dict], codes: set[str]) -> None:
    """Validate identities, null semantics and unique municipal periods before storage."""
    identities = set()
    for row in cells:
        key = row['code'], row['period']
        if row['code'] not in codes or key in identities:
            raise ValueError(f'Unknown/duplicate municipal cell: {key}')
        identities.add(key)
        if row['status'] not in {'observed', 'missing', 'suppressed'} or (row['value'] is not None) != (row['status'] == 'observed'):
            raise ValueError('Invalid normalized measurement state')
        for name in ['value', 'weight']:
            if row[name] is not None:
                normalize.number(row[name])


def validate_publication(document: dict) -> None:
    """Reject invalid identities and measurements before opening a database connection."""
    municipalities = document['municipalities']
    codes = {row['code'] for row in municipalities}
    if len(codes) != 118 or len(municipalities) != 118:
        raise ValueError('Section registry must contain exactly 118 municipalities')
    if any(len(code) != 6 or not code.isdigit() or not code.startswith('064') for code in codes):
        raise ValueError('Section registry contains an invalid ISTAT municipal code')
    metric_ids = set()
    for metric in document['metrics']:
        is_public_metric(metric)
        if metric['id'] in metric_ids:
            raise ValueError(f"Duplicate metric: {metric['id']}")
        metric_ids.add(metric['id'])
        validate_cells(metric['cells'], codes)
        validate_cells(metric.get('monthly', []), codes)
    definitions = {metric['id']: metric for metric in document['metrics']}
    for metric in document['metrics']:
        if metric.get('presentation_role') == 'supporting_breakdown':
            parent = definitions.get(metric.get('breakdown_parent'))
            if not parent or not is_public_metric(parent) or parent['category'] != metric['category'] or parent.get('breakdown_unit', parent['unit']) != metric['unit']:
                raise ValueError(f"Invalid breakdown parent: {metric['id']}")
        recipe = metric.get('recipe', {})
        related = recipe.get('related_history')
        if related is not None and related not in definitions:
            raise ValueError(f"Unknown historical companion: {related}")
        if recipe.get('show_companion_history') and not related:
            raise ValueError(f"Historical companion is not configured: {metric['id']}")
        if related is not None and definitions[related]['category'] != metric['category']:
            raise ValueError(f"Historical companion belongs to a different category: {related}")


def publish(document: dict) -> None:
    """Publish the selected store in one transaction, retaining the previous valid state on failure."""
    from etl.database import load_sections
    load_sections(document)


def build_map(root: Path = ROOT) -> None:
    """Simplify geometry for display only, preserving the source for statistical calculations."""
    from shapely.geometry import shape
    source = root / 'data/collection/municipal-boundaries.geojson'
    document = json.loads(source.read_text())
    shapes = [(feature['properties']['municipality_code'], shape(feature['geometry']).simplify(0.0005, preserve_topology=True)) for feature in document['features']]
    left = min(geometry.bounds[0] for _, geometry in shapes); right = max(geometry.bounds[2] for _, geometry in shapes)
    bottom = min(geometry.bounds[1] for _, geometry in shapes); top = max(geometry.bounds[3] for _, geometry in shapes)
    width = 600; height = (top-bottom) / ((right-left) * 0.755) * width
    def ring_path(ring):
        points = [(10+(x-left)/(right-left)*width, 10+(top-y)/(top-bottom)*height) for x,y in ring.coords]
        return 'M'+' L'.join(f'{x:.2f},{y:.2f}' for x,y in points)+' Z'
    features = []
    for code, geometry in shapes:
        polygons = [geometry] if geometry.geom_type == 'Polygon' else geometry.geoms
        path = ' '.join(ring_path(polygon.exterior)+' '+' '.join(ring_path(ring) for ring in polygon.interiors) for polygon in polygons)
        features.append({'code':code,'path':path})
    output = {'view_box': f'0 0 {width+20:.2f} {height+20:.2f}', 'features': features,
              'source': 'ISTAT municipal boundaries 1 January 2026', 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
    (root/'data/sections-map.json').write_text(json.dumps(output,separators=(',',':'))+'\n')


def ensure_map(root: Path = ROOT) -> None:
    """Reuse display geometry when its verified boundary input has not changed."""
    source = root / 'data/collection/municipal-boundaries.geojson'
    target = root / 'data/sections-map.json'
    with source.open('rb') as handle:
        expected = hashlib.file_digest(handle, 'sha256').hexdigest()
    if target.exists() and json.loads(target.read_text()).get('source_sha256') == expected:
        return
    try:
        build_map(root)
    except ImportError as error:
        raise ValueError('Rebuilding map geometry requires pip install -r requirements-collection.txt') from error


def write_report(document: dict, root: Path = ROOT) -> None:
    """Document the exact selected publication and its source-qualified coverage."""
    public = [metric for metric in document['metrics'] if is_public_metric(metric)]
    supporting = [metric for metric in document['metrics'] if not is_public_metric(metric)]
    lines = [
        '# Curated sections — publication inventory', '',
        f"Publication generated: {document['generated_at']}. This report is regenerated by `npm run data:sections`.", '',
        '## Publication and presentation', '',
        f"{len(public)} selected public metrics across {len(document['categories'])} sections use the same 118-municipality ISTAT registry. {len(supporting)} supporting series are stored separately from the public metric count. The selected store is independent of the legacy product database; both remain available.", '',
        'This publication backs provincial, municipal and comparison views. Public file exports are not provided.', '',
        'Configuration: `config/sections.json`. Normalization: `etl/section_normalization.py`. Publication: `etl/sections.py`. APIs: `/api/sections`, `/api/section`, `/api/section-map`, `/api/territory`. PostgreSQL schema: `sections`; portable SHA-256-verified snapshot: `data/sections.snapshot.json`.', '',
        '## Statistical rules', '',
        '- Latest means the latest available source period, not a claim that every measurement describes today. No municipality silently falls back to an older year in a latest-period map or table.',
        '- Weighted means retain same-period source denominators. Percentages without a usable denominator use an explicitly labelled municipal median, not an invented provincial percentage.',
        '- Province-wide historical lines use a constant cohort observed in every period. Its coverage is displayed and can differ from the latest headline. Missing municipal years remain gaps.',
        '- Historical IRPEF totals for archives without overall-income columns require all eight original disjoint income bins. Blank or suppressed bins invalidate the total and mean. The 2020–2024 stable cohort contains only 17 municipalities; latest 2024 covers 118. Amounts are nominal euros, without inflation correction.',
        '- PNRR projects are distinct CUP/local-project identities. Multi-location projects count once in the provincial total, so municipal counts must not be summed to reproduce that total. Cohesion projects use their original local-project identity and the export snapshot date.',
        '- Historical agriculture 1982–2010 excludes reconstructed Montoro predecessors and remains separate from census 2020. Holdings and land are assigned to headquarters; census definitions can change.',
        '- Soil stock 2024 and annual net consumption are separate measurements. Historical increments do not reconstruct historical stock; multi-year intervals are excluded from the annual series.',
        '- Climate uses ERA5-Land reanalysis at one interior sample point per municipality, not stations or municipal area averages. 2025 covers 118 points; 2020–2025 history covers ten. Complete daily coverage is required; monthly mean-temperature charts cover all 118 points in 2025. Null precipitation fields are excluded.',
        '- SIAT and MiC inventories have undated records. Absence of a mapped/listed item is unavailable, not evidence of zero assets. Library and pharmacy dates describe catalogue snapshots, not opening dates or verified real-time availability.',
        '- Privacy/anomaly flags and incomplete source categories preserve nulls. A zero must be observed in the source. No automatic source acquisition or scheduler activation is part of section publication.', '',
        '## Selected measurements', '',
        'Metric IDs are stable code identifiers. The public interface provides plain Italian labels. Latest coverage counts only usable numeric municipal cells; it does not prove census completeness. Each source link leads to the original publisher or verified distribution.', '',
    ]
    for category in document['categories']:
        lines.extend([f"### {category['id']}", '', '| Metric | Latest period | Latest coverage | Historical periods | Unit | Provincial summary | Sources |', '| --- | --- | --- | --- | --- | --- | --- |'])
        for metric in (metric for metric in public if metric['category'] == category['id']):
            latest = [row for row in metric['cells'] if row['period'] == metric['latest_period'] and row['status'] == 'observed'
                      and (metric['aggregation'] != 'weighted_mean' or row['weight'] is not None and row['weight'] > 0)]
            periods = metric['periods']
            history = f"{periods[0]}–{periods[-1]} ({len(periods)})" if len(periods) > 1 else 'Single period'
            sources = ', '.join(f"[{source['id']}]({source['url']})" for source in metric['sources'])
            lines.append(f"| `{metric['id']}` | {metric['latest_period']} | {len(latest)}/118 | {history} | {metric['unit']} | {metric['aggregation']} | {sources} |")
        lines.append('')
    if supporting:
        lines.extend(['## Supporting historical measurements', '',
                      'These source-qualified series support the corresponding public indicators. They are not additional public cards. Historical agriculture remains separate from census 2020; neither connecting lines nor 2010-to-2020 deltas are implied.', '',
                      '| Series | Periods | Observed cells | Unit | Sources |', '| --- | --- | --- | --- | --- |'])
        for metric in supporting:
            periods = metric['periods']
            observed = sum(row['status'] == 'observed' for row in metric['cells'])
            sources = ', '.join(f"[{source['id']}]({source['url']})" for source in metric['sources'])
            lines.append(f"| `{metric['id']}` | {', '.join(periods)} | {observed} | {metric['unit']} | {sources} |")
        lines.append('')
    lines.extend(['## Rebuild and portability', '',
                  '`npm run data:sections` transforms already acquired evidence without network access. Install `requirements-collection.txt` to rebuild display geometry. Failed validation preserves the previous PostgreSQL publication. Database publication uses a single transaction; database and portable filesystem artifacts are not one transaction.', '',
                  '`npm run db:seed` imports both verified snapshots through psycopg 3; it requires no acquisition or geographic dependencies. Python uses the private writer `DATABASE_URL`; Nitro uses the separate SELECT-only `DATABASE_READ_URL`. Use `data:update` for a complete coherent update or `data:rebuild` for existing staged evidence. No monthly scheduler is installed or enabled.', '',
                  'See [full availability](DATA_AVAILABILITY.md).', ''])
    (root / 'docs/SECTIONS.md').write_text('\n'.join(lines))


@contextmanager
def publication_lock():
    """Reject concurrent publishers while protecting the shared portable artifacts."""
    with (ROOT / 'data/sections.lock').open('a') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError('Another section publication is running') from error
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def read_snapshot(path: Path = SNAPSHOT) -> dict:
    """Read a portable selected publication only after checking its original SHA-256."""
    payload = path.read_bytes()
    expected = path.with_suffix('.sha256').read_text().split()[0]
    if hashlib.sha256(payload).hexdigest() != expected:
        raise ValueError('Section snapshot checksum mismatch')
    document = json.loads(payload)
    validate_publication(document)
    return document


def execute(restore: bool) -> None:
    """Build manually or restore the portable publication within the coordinator lock."""
    if restore:
        publish(read_snapshot())
    else:
        document = build()
        # Complete source validation precedes replacement of every published artifact.
        build_map()
        publish(document)
        encoded = json.dumps(document, ensure_ascii=False, separators=(',',':')).encode()
        temporary = SNAPSHOT.with_suffix('.pending'); temporary.write_bytes(encoded); os.replace(temporary, SNAPSHOT)
        SNAPSHOT.with_suffix('.sha256').write_text(hashlib.sha256(encoded).hexdigest()+'  '+SNAPSHOT.name+'\n')
        write_report(document)
    print('Section store published successfully.')


def main() -> None:
    """Serialize publishers without coupling publication to source acquisition."""
    parser = argparse.ArgumentParser(); parser.add_argument('--restore', action='store_true'); args = parser.parse_args()
    with publication_lock():
        execute(args.restore)


if __name__ == '__main__':
    main()
