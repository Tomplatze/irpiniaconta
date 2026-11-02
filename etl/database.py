"""PostgreSQL migrations and transactional publication of the two existing stores."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Iterable, Iterator

import psycopg
from psycopg import sql
from psycopg.types.json import Jsonb
from etl.models import AdapterResult
from etl.settings import environment_value

ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = ROOT / 'database/migrations'
MIGRATION_LOCK = 761402001
PUBLICATION_LOCK = 761402002


def connect(database_url: str | None = None) -> psycopg.Connection:
    """Use one server-side URL shared with Nitro; never print connection credentials."""
    url = database_url or environment_value('DATABASE_URL', ROOT)
    if not url:
        raise RuntimeError('DATABASE_URL is required. Configure the local .env file first.')
    return psycopg.connect(url, connect_timeout=10, application_name='atlante-irpinia-etl')


@contextmanager
def transaction(connection: psycopg.Connection | None = None) -> Iterator[psycopg.Connection]:
    """Commit an entire publication, or use a savepoint inside a caller-owned transaction."""
    if connection is not None:
        with connection.transaction():
            yield connection
        return
    with connect() as opened, opened.transaction():
        yield opened


def migrate(connection: psycopg.Connection | None = None) -> list[str]:
    """Apply ordered SQL files once and reject changes to already applied migrations."""
    files = sorted(MIGRATIONS.glob('[0-9]*_*.sql'), key=lambda path: int(path.name.split('_', 1)[0]))
    if not files:
        raise RuntimeError('No versioned SQL migrations were found.')
    versions = [path.name.split('_', 1)[0] for path in files]
    if len(set(versions)) != len(files):
        raise RuntimeError('Migration version numbers must be unique.')
    applied = []
    with transaction(connection) as database:
        database.execute('SELECT pg_advisory_xact_lock(%s)', (MIGRATION_LOCK,))
        database.execute('''CREATE TABLE IF NOT EXISTS public.schema_migrations (
            version text PRIMARY KEY, filename text NOT NULL, checksum text NOT NULL,
            applied_at timestamptz NOT NULL DEFAULT now())''')
        previous = {row[0]: row[1:] for row in database.execute(
            'SELECT version, filename, checksum FROM public.schema_migrations')}
        if previous.keys() - set(versions):
            raise RuntimeError('An applied migration file is missing. Restore the original migration.')
        if previous and any(int(version) <= max(map(int, previous)) for version in versions if version not in previous):
            raise RuntimeError('New migrations must follow the latest applied version. Add a higher version number.')
        for path, version in zip(files, versions):
            payload = path.read_bytes()
            checksum = hashlib.sha256(payload).hexdigest()
            if version in previous:
                if previous[version] != (path.name, checksum):
                    raise RuntimeError(f'Applied migration changed: {path.name}. Add a new migration instead.')
                continue
            database.execute(payload.decode('utf-8'))
            database.execute('INSERT INTO public.schema_migrations(version,filename,checksum) VALUES (%s,%s,%s)',
                             (version, path.name, checksum))
            applied.append(path.name)
    return applied


def require_current_schema(connection: psycopg.Connection | None = None) -> None:
    """Refuse imports against missing, pending or edited migrations without executing DDL."""
    with transaction(connection) as database:
        if database.execute("SELECT to_regclass('public.schema_migrations')").fetchone()[0] is None:
            raise RuntimeError('Database schema is not initialized. Run npm run db:migrate first.')
        applied = {row[0]: (row[1], row[2]) for row in database.execute(
            'SELECT version,filename,checksum FROM public.schema_migrations')}
        expected = {path.name.split('_', 1)[0]: (path.name, hashlib.sha256(path.read_bytes()).hexdigest())
                    for path in MIGRATIONS.glob('[0-9]*_*.sql')}
        if applied != expected:
            raise RuntimeError('Database migrations are pending or changed. Run npm run db:migrate; restore edited applied files first.')


def semantic_checksum(value: object) -> str:
    """Hash canonical JSON values rather than incidental key order or whitespace."""
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def last_import_checksum(connection: psycopg.Connection, dataset_key: str) -> str | None:
    """Find the most recent committed version, retaining failed attempts independently."""
    row = connection.execute('''SELECT checksum FROM atlas.dataset_imports
        WHERE dataset_key=%s AND status IN ('success','unchanged') ORDER BY id DESC LIMIT 1''',
        (dataset_key,)).fetchone()
    return row[0] if row else None


def record_import(connection: psycopg.Connection, *, dataset_key: str, source_name: str,
                  checksum: str, status: str, source_url: str | None = None,
                  source_version: str | None = None, reference_period: str | None = None,
                  published_at: datetime | str | None = None, records_processed: int = 0,
                  records_inserted: int = 0, records_updated: int = 0, records_rejected: int = 0,
                  error_message: str | None = None, started_at: datetime | None = None) -> int:
    """Separate reference period, original publication date and actual import timestamps."""
    row = connection.execute('''INSERT INTO atlas.dataset_imports
        (dataset_key,source_name,source_url,source_version,reference_period,published_at,
         started_at,completed_at,imported_at,records_processed,records_inserted,records_updated,
         records_rejected,status,checksum,error_message)
        VALUES (%s,%s,%s,%s,%s,%s,COALESCE(%s,statement_timestamp()),clock_timestamp(),
                CASE WHEN %s='failed' THEN NULL ELSE clock_timestamp() END,%s,%s,%s,%s,%s,%s,%s) RETURNING id''',
        (dataset_key, source_name, source_url, source_version, reference_period, published_at,
         started_at, status,
         records_processed, records_inserted, records_updated, records_rejected, status,
         checksum, error_message)).fetchone()
    return row[0]


def copy_rows(connection: psycopg.Connection, schema: str, table: str,
              columns: list[str], rows: Iterable[tuple]) -> None:
    """Bulk-load explicit publication columns; identifiers never come from source input."""
    statement = sql.SQL('COPY {}.{} ({}) FROM STDIN').format(
        sql.Identifier(schema), sql.Identifier(table), sql.SQL(',').join(map(sql.Identifier, columns)))
    with connection.cursor().copy(statement) as copy:
        for row in rows:
            copy.write_row(row)


def _counts(previous: dict, current: dict) -> tuple[int, int]:
    """Count logical record additions and revisions, independent of physical replacement."""
    inserted = len(current.keys() - previous.keys())
    updated = sum(previous[key] != value for key, value in current.items() if key in previous)
    return inserted, updated


def _failure(dataset_key: str, checksum: str, error: Exception, processed: int) -> None:
    """Keep a failed attempt after rollback without masking the original database error."""
    try:
        with connect() as database:
            record_import(database, dataset_key=dataset_key, source_name=dataset_key,
                          checksum=checksum, status='failed', records_processed=processed,
                          records_rejected=processed, error_message=f'{type(error).__name__}: {error}')
    except (psycopg.Error, RuntimeError):
        # A disconnected database cannot record its own outage; the caller still receives the error.
        pass


def load_core(municipalities: list[dict], results: list[AdapterResult], report: dict,
              connection: psycopg.Connection | None = None, *, scope: dict | None = None) -> None:
    """Publish validated core records atomically while retaining all acquisition history."""
    from etl.quality import assess, validate_registry
    codes = validate_registry(municipalities)
    for item in results:
        assess(item, codes)
    scope = scope if scope is not None else json.loads((ROOT / 'config/sources.json').read_text())
    payload = [{'metadata': item.metadata, 'observations': [asdict(row) for row in item.observations],
                'entities': [asdict(row) for row in item.entities]} for item in results]
    checksum = semantic_checksum({'municipalities': municipalities, 'datasets': payload, 'scope': scope})
    processed = sum(len(item.observations) + len(item.entities) for item in results)
    try:
        with transaction(connection) as database:
            require_current_schema(database)
            started_at = database.execute('SELECT clock_timestamp()').fetchone()[0]
            database.execute('SELECT pg_advisory_xact_lock(%s)', (PUBLICATION_LOCK,))
            previous_observations = {(row[0], row[1], row[2]): row[3:] for row in database.execute(
                'SELECT municipality_code,indicator_id,period,value,status FROM atlas.observations')}
            previous_entities = {(row[0], row[1]): row[2:] for row in database.execute(
                'SELECT dataset_id,source_id,municipality_code,title,kind,period,payload FROM atlas.entities')}
            previous_checksums = {item.metadata['id']: last_import_checksum(database, 'atlas.' + item.metadata['id'])
                                  for item in results}
            _replace_core(database, municipalities, results, scope)
            database.execute('''INSERT INTO atlas.ingestion_runs(id,started_at,completed_at,mode,report)
                VALUES (%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING''',
                (report['run_id'], report['started_at'], report['completed_at'], report['mode'], Jsonb(report)))
            for item, content in zip(results, payload):
                metadata = item.metadata
                current = {('observation', row.municipality_code, row.indicator_id, row.period): (row.value, row.status)
                           for row in item.observations}
                current.update({('entity', row.dataset_id, row.source_id):
                                (row.municipality_code, row.title, row.kind, row.period, row.payload) for row in item.entities})
                old = {('observation', *key): value for key, value in previous_observations.items()
                       if key[1] in {indicator['id'] for indicator in metadata['indicators']}}
                old.update({('entity', *key): value for key, value in previous_entities.items() if key[0] == metadata['id']})
                inserted, updated = _counts(old, current)
                digest = semantic_checksum(content)
                record_import(database, dataset_key='atlas.' + metadata['id'], source_name=metadata['name'],
                              source_url=metadata.get('download_url') or metadata.get('landing_url'),
                              source_version=metadata.get('version'), reference_period=str(metadata.get('period', '')),
                              checksum=digest, status='unchanged' if previous_checksums[metadata['id']] == digest else 'success',
                              records_processed=len(current), records_inserted=inserted, records_updated=updated,
                              started_at=started_at)
            record_import(database, dataset_key='atlas-publication', source_name='Core normalized publication',
                          checksum=checksum, status='success', records_processed=processed, started_at=started_at)
    except Exception as error:
        if connection is None:
            _failure('atlas-publication', checksum, error, processed)
        raise


def _replace_core(database: psycopg.Connection, municipalities: list[dict], results: list[AdapterResult], scope: dict) -> None:
    """Replace measurement tables with COPY; upsert small metadata tables in the same transaction."""
    database.execute('DELETE FROM atlas.observations')
    database.execute('DELETE FROM atlas.entities')
    database.execute('DELETE FROM atlas.indicators')
    with database.cursor() as cursor:
        cursor.executemany('''INSERT INTO atlas.municipalities VALUES (%s,%s,%s,%s)
            ON CONFLICT(code) DO UPDATE SET name=excluded.name,province_code=excluded.province_code,region_code=excluded.region_code''',
            [(row['code'], row['name'], row['province_code'], row['region_code']) for row in municipalities])
        cursor.executemany('''INSERT INTO atlas.datasets VALUES (%s,%s,%s,%s,%s)
            ON CONFLICT(id) DO UPDATE SET metadata=excluded.metadata,status=excluded.status,verified_at=excluded.verified_at,position=excluded.position''',
            [(item.metadata['id'], Jsonb(item.metadata), item.metadata['status'], item.metadata['verified_at'], index)
             for index, item in enumerate(results, 1)])
        cursor.executemany('''INSERT INTO atlas.categories VALUES (%s,%s,%s)
            ON CONFLICT(id) DO UPDATE SET metadata=excluded.metadata,position=excluded.position''',
            [(row['id'], Jsonb(row), index) for index, row in enumerate(scope['categories'], 1)])
        cursor.executemany('''INSERT INTO atlas.source_registry VALUES (%s,%s,%s,%s)
            ON CONFLICT(id) DO UPDATE SET category_id=excluded.category_id,metadata=excluded.metadata,position=excluded.position''',
            [(row['id'], row['category_id'], Jsonb(row), index) for index, row in enumerate(scope['sources'], 1)])
    indicator_rows = [(metric['id'], item.metadata['id'], metric['label'], metric['unit'], metric['definition'])
                      for item in results for metric in item.metadata['indicators']]
    copy_rows(database, 'atlas', 'indicators', ['id','dataset_id','label','unit','definition','position'],
              [(*row, index) for index, row in enumerate(indicator_rows, 1)])
    copy_rows(database, 'atlas', 'observations', ['municipality_code','indicator_id','period','value','status'],
              ((row.municipality_code, row.indicator_id, row.period, row.value, row.status)
               for item in results for row in item.observations))
    entity_rows = [(row.dataset_id, row.source_id, row.municipality_code, row.title, row.kind, row.period, Jsonb(row.payload))
                   for item in results for row in item.entities]
    copy_rows(database, 'atlas', 'entities', ['dataset_id','source_id','municipality_code','title','kind','period','payload','position'],
              [(*row, index) for index, row in enumerate(entity_rows, 1)])
    database.execute('DELETE FROM atlas.datasets WHERE NOT(id=ANY(%s))', ([item.metadata['id'] for item in results],))
    database.execute('DELETE FROM atlas.source_registry WHERE NOT(id=ANY(%s))', ([row['id'] for row in scope['sources']],))
    database.execute('DELETE FROM atlas.categories WHERE NOT(id=ANY(%s))', ([row['id'] for row in scope['categories']],))
    database.execute('DELETE FROM atlas.municipalities WHERE NOT(code=ANY(%s))', ([row['code'] for row in municipalities],))


def load_sections(document: dict, connection: psycopg.Connection | None = None) -> None:
    """Publish curated metrics and their weights together, preserving last-valid data on failure."""
    from etl.sections import validate_publication
    validate_publication(document)
    checksum = semantic_checksum(document)
    processed = sum(len(metric['cells']) + len(metric.get('monthly', [])) for metric in document['metrics'])
    try:
        with transaction(connection) as database:
            require_current_schema(database)
            started_at = database.execute('SELECT clock_timestamp()').fetchone()[0]
            database.execute('SELECT pg_advisory_xact_lock(%s)', (PUBLICATION_LOCK,))
            previous = {}
            for table in ['values_annual', 'values_monthly']:
                previous[table] = {(row[0], row[1], row[2]): row[3:] for row in database.execute(
                    sql.SQL('SELECT metric,code,period,value,status,weight FROM sections.{}').format(sql.Identifier(table)))}
            previous_checksums = {metric['id']: last_import_checksum(database, 'sections.' + metric['id'])
                                  for metric in document['metrics']}
            _replace_sections(database, document)
            for metric in document['metrics']:
                current = {(table, row['code'], row['period']): (row['value'], row['status'], row['weight'])
                           for table, part in [('values_annual','cells'), ('values_monthly','monthly')]
                           for row in metric.get(part, [])}
                old = {(table, key[1], key[2]): value for table, values in previous.items()
                       for key, value in values.items() if key[0] == metric['id']}
                inserted, updated = _counts(old, current)
                digest = semantic_checksum(metric)
                source = metric['sources'][0] if metric.get('sources') else {}
                record_import(database, dataset_key='sections.' + metric['id'], source_name=metric['label'],
                              source_url=source.get('url'), reference_period=metric.get('latest_period'), checksum=digest,
                              status='unchanged' if previous_checksums[metric['id']] == digest else 'success',
                              records_processed=len(current), records_inserted=inserted, records_updated=updated,
                              started_at=started_at)
            record_import(database, dataset_key='sections-publication', source_name='Curated sections publication',
                          checksum=checksum, status='success', records_processed=processed, started_at=started_at)
    except Exception as error:
        if connection is None:
            _failure('sections-publication', checksum, error, processed)
        raise


def _replace_sections(database: psycopg.Connection, document: dict) -> None:
    """Keep the existing selected-store contract and authored order without an ORM."""
    for table in ['values_annual', 'values_monthly', 'metrics', 'categories', 'municipalities', 'publication']:
        database.execute(sql.SQL('DELETE FROM sections.{}').format(sql.Identifier(table)))
    copy_rows(database, 'sections', 'municipalities', ['code','name'],
              [(row['code'], row['name']) for row in document['municipalities']])
    copy_rows(database, 'sections', 'categories', ['id','metadata','position'],
              [(row['id'], Jsonb(row), index) for index, row in enumerate(document['categories'], 1)])
    for index, metric in enumerate(document['metrics'], 1):
        metadata = {key: value for key, value in metric.items() if key not in {'cells','monthly'}}
        metadata['has_monthly'] = bool(metric.get('monthly'))
        database.execute('INSERT INTO sections.metrics VALUES (%s,%s,%s,%s)',
                         (metric['id'], metric['category'], Jsonb(metadata), index))
        for table, part in [('values_annual','cells'), ('values_monthly','monthly')]:
            copy_rows(database, 'sections', table, ['metric','code','period','value','status','weight'],
                      [(metric['id'], row['code'], row['period'], row['value'], row['status'], row['weight'])
                       for row in metric.get(part, [])])
    database.execute('INSERT INTO sections.publication VALUES (%s)',
                     (Jsonb({key: document[key] for key in ['generated_at','lineage']}),))


def main() -> None:
    """Apply schema migrations explicitly, separately from all dataset imports."""
    argparse.ArgumentParser(description=__doc__).parse_args()
    applied = migrate()
    print(json.dumps({'applied_migrations': applied, 'status': 'ready'}, indent=2))


if __name__ == '__main__':
    main()
