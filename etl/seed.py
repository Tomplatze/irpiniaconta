"""Restore verified local publications atomically, without downloading source data."""
import json

from psycopg.types.json import Jsonb

from etl.database import PUBLICATION_LOCK, connect, load_core, load_sections, require_current_schema
from etl.pipeline import ROOT, replay_snapshot
from etl.publication_assets import publish_assets
from etl.publication import load_prepared
from etl.seed_validation import assert_seed_compatible


def main() -> None:
    """Validate all local evidence before replacing either publication or its downloads."""
    if not (ROOT / 'data/snapshot.json').is_file():
        raise SystemExit('Local publication is missing. Run npm run data:unpack -- /path/to/data.tar.gz first. See data/README.md.')
    prepared = load_prepared(ROOT)
    municipalities, datasets, report = prepared.municipalities, prepared.datasets, prepared.report
    selected, assets = prepared.selected, prepared.assets
    reports = [report]
    for path in sorted((ROOT / 'data/history').glob('*/snapshot.json')):
        _, _, historical_report = replay_snapshot(path)
        reports.append(historical_report)
    with connect() as database, database.transaction():
        require_current_schema(database)
        database.execute('SELECT pg_advisory_xact_lock(%s)', (PUBLICATION_LOCK,))
        assert_seed_compatible(database, municipalities, datasets, selected, assets)
        load_core(municipalities, datasets, report, connection=database)
        load_sections(selected, connection=database)
        for historical in reports:
            database.execute('''INSERT INTO atlas.ingestion_runs(id,started_at,completed_at,mode,report)
                VALUES (%s,%s,%s,%s,%s) ON CONFLICT(id) DO NOTHING''',
                (historical['run_id'], historical['started_at'], historical['completed_at'],
                 historical['mode'], Jsonb(historical)))
        asset_result = publish_assets(connection=database, assets=assets)
    print(json.dumps({'status': 'ready', 'municipalities': len(municipalities),
                      'selected_metrics': len(selected['metrics']), 'assets': asset_result}, indent=2))


if __name__ == '__main__':
    main()
