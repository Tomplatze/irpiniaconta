"""Explicit, lossless one-time migration of the retained SQLite publications."""
from __future__ import annotations

import argparse
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3

from psycopg import sql
from psycopg.types.json import Jsonb

from etl.database import PUBLICATION_LOCK, ROOT, connect, copy_rows, record_import, require_current_schema, semantic_checksum

TABLES = {
    'atlas': ['municipalities', 'datasets', 'indicators', 'observations', 'ingestion_runs',
              'categories', 'source_registry', 'entities'],
    'sections': ['municipalities', 'categories', 'metrics', 'values_annual', 'values_monthly', 'publication'],
}
ORDERED = {'atlas': {'datasets','indicators','categories','source_registry','entities'},
           'sections': {'categories','metrics'}}
JSON_COLUMNS = {'metadata','payload','report'}


def read_legacy(path: Path, schema: str) -> dict:
    """Read original values and SQLite row order without opening the source for writing."""
    if not path.is_file():
        raise FileNotFoundError(f'Legacy SQLite publication not found: {path}')
    with closing(sqlite3.connect(f'{path.resolve().as_uri()}?mode=ro', uri=True)) as source:
        if source.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or source.execute('PRAGMA foreign_key_check').fetchall():
            raise ValueError(f'Legacy database integrity failed: {path.name}')
        present = {row[0] for row in source.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
        if present != set(TABLES[schema]):
            raise ValueError(f'Unexpected legacy tables in {path.name}: {sorted(present.symmetric_difference(TABLES[schema]))}')
        tables = {}
        for table in TABLES[schema]:
            columns = [row[1] for row in source.execute(f'PRAGMA table_info("{table}")')]
            rows = source.execute(f'SELECT * FROM "{table}" ORDER BY rowid').fetchall()
            decoded = [tuple(json.loads(value) if column in JSON_COLUMNS else value
                             for column, value in zip(columns, row)) for row in rows]
            tables[table] = {'columns': columns, 'rows': decoded}
        if len(tables['municipalities']['rows']) != 118:
            raise ValueError('Legacy registry must contain exactly 118 municipalities')
    return tables


def table_digest(rows: list[tuple]) -> str:
    """Compare all original columns with canonical JSON, independent of database physical order."""
    encoded = sorted(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
                     for row in rows)
    return hashlib.sha256('\n'.join(encoded).encode('utf-8')).hexdigest()


def inspect_target(connection, schema: str, tables: dict) -> dict:
    """Return per-table count/digest evidence, including preserved authored order."""
    comparison = {}
    for table, content in tables.items():
        query = sql.SQL('SELECT {} FROM {}.{}').format(
            sql.SQL(',').join(map(sql.Identifier, content['columns'])), sql.Identifier(schema), sql.Identifier(table))
        if table in ORDERED[schema]:
            query += sql.SQL(' ORDER BY position')
        actual = connection.execute(query).fetchall()
        expected = content['rows']
        expected_digest = table_digest(expected)
        actual_digest = table_digest(actual)
        row = {'source_count': len(expected), 'target_count': len(actual), 'source_sha256': expected_digest,
               'target_sha256': actual_digest, 'matches': expected_digest == actual_digest and len(actual) == len(expected)}
        if table in ORDERED[schema]:
            row['order_matches'] = actual == expected
            row['matches'] = row['matches'] and row['order_matches']
        comparison[table] = row
    return comparison


def backup_sources(core: Path, sections: Path, destination: Path) -> dict:
    """Keep consistent SQLite copies and hashes before changing PostgreSQL."""
    destination.mkdir(parents=True, exist_ok=False)
    manifest = {'created_at': datetime.now(timezone.utc).isoformat(), 'files': []}
    for path in [core, sections]:
        target = destination / path.name
        with closing(sqlite3.connect(f'{path.resolve().as_uri()}?mode=ro', uri=True)) as source, closing(sqlite3.connect(target)) as copy:
            source.backup(copy)
            copy.commit()
        manifest['files'].append({'source': str(path.resolve()), 'backup': str(target.resolve()),
                                  'bytes': target.stat().st_size, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


def copy_legacy(connection, schema: str, tables: dict) -> None:
    """Copy original table columns and retained row order inside the caller's transaction."""
    for table, content in tables.items():
        columns = list(content['columns'])
        rows = [tuple(Jsonb(value) if column in JSON_COLUMNS else value for column, value in zip(columns, row))
                for row in content['rows']]
        if table in ORDERED[schema]:
            columns.append('position')
            rows = [(*row, index) for index, row in enumerate(rows, 1)]
        copy_rows(connection, schema, table, columns, rows)


def migrate_legacy(core: Path, sections: Path, *, backup_directory: Path | None = None) -> dict:
    """Migrate both stores in one transaction, refusing to overwrite a different populated target."""
    sources = {'atlas': read_legacy(core, 'atlas'), 'sections': read_legacy(sections, 'sections')}
    core_names = {row[0]: row[1] for row in sources['atlas']['municipalities']['rows']}
    if core_names != {row[0]: row[1] for row in sources['sections']['municipalities']['rows']}:
        raise ValueError('The two legacy registries disagree.')
    destination = backup_directory or ROOT / 'data/backups' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ-sqlite-import')
    backup = backup_sources(core, sections, destination)
    digest = semantic_checksum({schema: {table: table_digest(content['rows']) for table, content in tables.items()}
                                for schema, tables in sources.items()})
    report = {'started_at': datetime.now(timezone.utc).isoformat(), 'backup': backup, 'schemas': {}, 'status': 'success'}
    try:
        with connect() as connection, connection.transaction():
            require_current_schema(connection)
            connection.execute('SELECT pg_advisory_xact_lock(%s)', (PUBLICATION_LOCK,))
            before = {schema: inspect_target(connection, schema, tables) for schema, tables in sources.items()}
            already_matches = all(row['matches'] for tables in before.values() for row in tables.values())
            target_empty = all(row['target_count'] == 0 for tables in before.values() for row in tables.values())
            if not already_matches and not target_empty:
                raise ValueError('PostgreSQL already contains different publication data. No records were overwritten; back up and review the target first.')
            if not already_matches:
                for schema, tables in sources.items():
                    copy_legacy(connection, schema, tables)
            report['schemas'] = {schema: inspect_target(connection, schema, tables) for schema, tables in sources.items()}
            if not all(row['matches'] for tables in report['schemas'].values() for row in tables.values()):
                raise ValueError('A migrated table differs from SQLite. The entire import was rolled back.')
            for schema, tables in sources.items():
                count = sum(len(content['rows']) for content in tables.values())
                record_import(connection, dataset_key='sqlite.' + schema, source_name=f'Original {schema} SQLite publication',
                              source_version=hashlib.sha256((core if schema == 'atlas' else sections).read_bytes()).hexdigest(),
                              checksum=digest, status='unchanged' if already_matches else 'success', records_processed=count,
                              records_inserted=0 if already_matches else count)
            report['status'] = 'unchanged' if already_matches else 'success'
    except Exception as error:
        report.update({'status': 'failed', 'error': f'{type(error).__name__}: {error}'})
        (destination / 'migration-report.json').write_text(json.dumps(report, indent=2) + '\n')
        try:
            with connect() as connection:
                record_import(connection, dataset_key='sqlite-migration', source_name='Original SQLite publications',
                              checksum=digest, status='failed', error_message=report['error'])
        except Exception:
            pass
        raise
    report['completed_at'] = datetime.now(timezone.utc).isoformat()
    (destination / 'migration-report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main() -> None:
    """Require prior schema migrations and keep a reviewable full comparison report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--core', type=Path, default=ROOT / 'data/atlas.sqlite')
    parser.add_argument('--sections', type=Path, default=ROOT / 'data/sections.sqlite')
    parser.add_argument('--backup-directory', type=Path)
    parser.add_argument('--output', type=Path)
    arguments = parser.parse_args()
    report = migrate_legacy(arguments.core, arguments.sections, backup_directory=arguments.backup_directory)
    if arguments.output:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
