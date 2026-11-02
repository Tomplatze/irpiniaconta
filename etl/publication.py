"""Publish a complete prepared dataset revision in one PostgreSQL transaction."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import psycopg

from etl.database import PUBLICATION_LOCK, connect, load_core, load_sections, record_import, require_current_schema
from etl.models import AdapterResult
from etl.pipeline import replay_snapshot
from etl.publication_assets import load_assets, publish_assets
from etl.quality import assess, validate_registry
from etl.registry import load_scope
from etl.sections import read_snapshot
from etl.workspaces import file_hash, run_path


@dataclass
class PreparedPublication:
    """Validated inputs shared by restore and update, independent of source acquisition."""

    municipalities: list[dict]
    datasets: list[AdapterResult]
    report: dict
    selected: dict
    assets: tuple[dict, dict]
    scope: dict


def load_prepared(root: Path) -> PreparedPublication:
    """Validate all persisted inputs before the first database write."""
    municipalities, datasets, report = replay_snapshot(root / 'data/snapshot.json')
    codes = validate_registry(municipalities)
    for dataset in datasets:
        assess(dataset, codes)
    selected = read_snapshot(root / 'data/sections.snapshot.json')
    if municipalities != selected['municipalities']:
        raise ValueError('Prepared municipal registries disagree')
    for key, name in [('product_snapshot_sha256', 'data/snapshot.json'),
                      ('collection_inventory_sha256', 'data/collection/inventory.json'),
                      ('configuration_sha256', 'config/sections.json')]:
        if selected['lineage'][key] != file_hash(root / name):
            raise ValueError(f'Prepared lineage mismatch: {name}')
    return PreparedPublication(municipalities, datasets, report, selected, load_assets(root), load_scope(root))


def revision(connection: psycopg.Connection) -> list[int]:
    """Detect intervening writes by any supported publisher before replacing a prepared revision."""
    return list(connection.execute('SELECT COALESCE(MAX(id),0),COUNT(*) FROM atlas.dataset_imports').fetchone())


def baseline(root: Path | None = None) -> list[int]:
    """Require an explicit schema setup before preparation; never migrate during ingestion."""
    with connect() as connection:
        require_current_schema(connection)
        if root is not None:
            committed = connection.execute(
                "SELECT dataset_key FROM atlas.dataset_imports WHERE dataset_key LIKE 'workflow/%'").fetchall()
            for (key,) in committed:
                identity = key.removeprefix('workflow/')
                report = run_path(root, identity) / 'run.json'
                if report.is_file() and json.loads(report.read_text())['status'] != 'published':
                    raise ValueError(f'Recover committed run {identity} with data:publish before preparing another update')
        return revision(connection)


def publish_prepared(prepared: PreparedPublication, *, identity: str, checksum: str,
                     expected_revision: list[int], connection: psycopg.Connection | None = None) -> dict:
    """Commit core, selected metrics, documents and artifacts together, or roll back everything."""
    from etl.database import transaction

    with transaction(connection) as database:
        require_current_schema(database)
        database.execute('SELECT pg_advisory_xact_lock(%s)', (PUBLICATION_LOCK,))
        marker = database.execute('SELECT checksum,id FROM atlas.dataset_imports WHERE dataset_key=%s',
                                  ('workflow/' + identity,)).fetchone()
        if marker:
            if marker[0] != checksum:
                raise ValueError('Run identifier already belongs to a different prepared publication')
            if revision(database)[0] != marker[1]:
                raise ValueError('A newer import exists; refusing to promote files from an older committed run')
            return {'status': 'already_committed'}
        if revision(database) != expected_revision:
            raise ValueError('Database changed after preparation; prepare a new run')
        configured = {item.metadata['source_id'] for item in prepared.datasets}
        retained = {row[0] for row in database.execute('SELECT id FROM atlas.source_registry')}
        if retained - configured:
            raise ValueError('Previously published sources were removed. Disable them with enabled=false instead')
        load_core(prepared.municipalities, prepared.datasets, prepared.report, connection=database, scope=prepared.scope)
        load_sections(prepared.selected, connection=database)
        result = publish_assets(connection=database, assets=prepared.assets)
        record_import(database, dataset_key='workflow/' + identity, source_name='Complete prepared publication',
                      checksum=checksum, status='success', records_processed=len(prepared.datasets) + len(prepared.selected['metrics']))
        return {'status': 'committed', 'assets': result}
