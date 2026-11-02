"""Validated PostgreSQL ingestion and reproducible normalized-snapshot replay."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import uuid

from etl.models import AdapterResult, Observation, Entity

ROOT = Path(__file__).resolve().parent.parent


def utc_now() -> str:
    """Return an unambiguous acquisition timestamp."""
    return datetime.now(timezone.utc).isoformat()


def write_database(municipalities: list[dict[str, str]], results: list[AdapterResult], report: dict[str, object]) -> None:
    """Validate and publish the complete core store in one PostgreSQL transaction."""
    from etl.database import load_core
    load_core(municipalities, results, report)


def replay_snapshot(snapshot: Path) -> tuple[list[dict[str, str]], list[AdapterResult], dict[str, object]]:
    """Rebuild from an explicitly labelled normalized snapshot after hash verification."""
    payload = snapshot.read_bytes()
    expected = snapshot.with_suffix('.sha256').read_text().strip()
    if hashlib.sha256(payload).hexdigest() != expected:
        raise RuntimeError('Normalized snapshot checksum mismatch')
    content = json.loads(payload)
    results = [AdapterResult(row['metadata'], [Observation(**value) for value in row['observations']], entities=[Entity(**value) for value in row.get('entities', [])]) for row in content['datasets']]
    return content['municipalities'], results, content['report']


def execute(offline: bool = False, snapshot_mode: bool = False) -> dict[str, object]:
    """Delegate acquisition to the central registry or replay the verified snapshot."""
    snapshot = ROOT / 'data/snapshot.json'
    if snapshot_mode:
        municipalities, results, source_report = replay_snapshot(snapshot)
        report = {**source_report, 'run_id': str(uuid.uuid4()), 'mode': 'snapshot',
                  'snapshot_source_run_id': source_report['run_id'],
                  'started_at': utc_now(), 'completed_at': utc_now()}
        write_database(municipalities, results, report)
        return report
    from etl.refresh import execute as refresh
    return refresh(offline=offline)



def main() -> None:
    """Run ingestion from the command line without mutating reference sources."""
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--offline', action='store_true', help='Reparse locally downloaded full source artifacts')
    modes.add_argument('--snapshot', action='store_true', help='Restore bundled normalized data without network access')
    arguments = parser.parse_args()
    report = execute(arguments.offline, arguments.snapshot)
    print(json.dumps({'database': 'PostgreSQL',
                      'mode': report['mode'], 'municipalities': report['municipality_count'],
                      'ready_sources': sum(row['status'] == 'ready' for row in report['quality'])}, indent=2))


if __name__ == '__main__':
    main()
