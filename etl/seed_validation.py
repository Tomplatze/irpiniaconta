"""Reject snapshot seeding when it would replace a different published dataset."""
import json

import psycopg

from etl.database import ROOT


def _assert_group(connection: psycopg.Connection, name: str, tables: list[tuple[str, str, list]]) -> None:
    """Permit an empty publication or require every original column and authored order to match."""
    actual = [(table, connection.execute(query).fetchall(), expected) for table, query, expected in tables]
    if all(not rows for _, rows, _ in actual):
        return
    for table, rows, expected in actual:
        if rows != expected:
            raise ValueError(f'Refusing seed: {name}.{table} differs from the bundled publication. '
                             'Existing data were not changed. Back up and review the database before importing a replacement.')


def assert_seed_compatible(connection: psycopg.Connection, municipalities: list[dict], results: list,
                           selected: dict, assets: tuple[dict, dict]) -> None:
    """Read only: refuse changes to any populated publication, while allowing initial or identical seeds."""
    scope = json.loads((ROOT / 'config/sources.json').read_text())
    indicators = [(metric['id'], result.metadata['id'], metric['label'], metric['unit'], metric['definition'])
                  for result in results for metric in result.metadata['indicators']]
    entities = [(row.dataset_id, row.source_id, row.municipality_code, row.title, row.kind, row.period, row.payload)
                for result in results for row in result.entities]
    observations = [(row.municipality_code, row.indicator_id, row.period, row.value, row.status)
                    for result in results for row in result.observations]
    _assert_group(connection, 'atlas', [
        ('municipalities', 'SELECT code,name,province_code,region_code FROM atlas.municipalities ORDER BY code COLLATE "C"',
         sorted([(row['code'], row['name'], row['province_code'], row['region_code']) for row in municipalities])),
        ('datasets', 'SELECT id,metadata,status,verified_at,position FROM atlas.datasets ORDER BY position',
         [(row.metadata['id'], row.metadata, row.metadata['status'], row.metadata['verified_at'], index)
          for index, row in enumerate(results, 1)]),
        ('indicators', 'SELECT id,dataset_id,label,unit,definition,position FROM atlas.indicators ORDER BY position',
         [(*row, index) for index, row in enumerate(indicators, 1)]),
        ('observations', 'SELECT municipality_code,indicator_id,period,value,status FROM atlas.observations ORDER BY municipality_code COLLATE "C",indicator_id COLLATE "C",period COLLATE "C"',
         sorted(observations, key=lambda row: row[:3])),
        ('entities', 'SELECT dataset_id,source_id,municipality_code,title,kind,period,payload,position FROM atlas.entities ORDER BY position',
         [(*row, index) for index, row in enumerate(entities, 1)]),
        ('categories', 'SELECT id,metadata,position FROM atlas.categories ORDER BY position',
         [(row['id'], row, index) for index, row in enumerate(scope['categories'], 1)]),
        ('source_registry', 'SELECT id,category_id,metadata,position FROM atlas.source_registry ORDER BY position',
         [(row['id'], row['category_id'], row, index) for index, row in enumerate(scope['sources'], 1)]),
    ])

    metrics = []
    for index, metric in enumerate(selected['metrics'], 1):
        metadata = {key: value for key, value in metric.items() if key not in {'cells', 'monthly'}}
        metadata['has_monthly'] = bool(metric.get('monthly'))
        metrics.append((metric['id'], metric['category'], metadata, index))
    cells = {
        table: sorted([(metric['id'], row['code'], row['period'], row['value'], row['status'], row['weight'])
                       for metric in selected['metrics'] for row in metric.get(part, [])], key=lambda row: row[:3])
        for table, part in [('values_annual', 'cells'), ('values_monthly', 'monthly')]
    }
    _assert_group(connection, 'sections', [
        ('municipalities', 'SELECT code,name FROM sections.municipalities ORDER BY code COLLATE "C"',
         sorted([(row['code'], row['name']) for row in selected['municipalities']])),
        ('categories', 'SELECT id,metadata,position FROM sections.categories ORDER BY position',
         [(row['id'], row, index) for index, row in enumerate(selected['categories'], 1)]),
        ('metrics', 'SELECT id,category,metadata,position FROM sections.metrics ORDER BY position', metrics),
        ('values_annual', 'SELECT metric,code,period,value,status,weight FROM sections.values_annual ORDER BY metric COLLATE "C",code COLLATE "C",period COLLATE "C"', cells['values_annual']),
        ('values_monthly', 'SELECT metric,code,period,value,status,weight FROM sections.values_monthly ORDER BY metric COLLATE "C",code COLLATE "C",period COLLATE "C"', cells['values_monthly']),
        ('publication', 'SELECT metadata FROM sections.publication',
         [({key: selected[key] for key in ['generated_at', 'lineage']},)]),
    ])

    documents, artifacts = assets
    _assert_group(connection, 'assets', [
        ('publication_documents', 'SELECT key,document FROM atlas.publication_documents ORDER BY key COLLATE "C"',
         sorted(documents.items())),
        ('publication_artifacts', 'SELECT path,sha256,kind FROM atlas.publication_artifacts ORDER BY path COLLATE "C"',
         sorted((path, row['sha256'], row['kind']) for path, row in artifacts.items())),
    ])
