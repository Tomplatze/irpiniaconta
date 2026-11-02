"""Verify that initial-data seeding cannot replace newer or different publications."""
import os
from pathlib import Path
import unittest
from unittest.mock import Mock

from etl.database import PUBLICATION_LOCK, ROOT, connect
from etl.pipeline import replay_snapshot
from etl.publication_assets import load_assets
from etl.sections import read_snapshot
from etl.seed_validation import _assert_group, assert_seed_compatible


class EmptySeedTests(unittest.TestCase):
    def test_wholly_empty_group_is_allowed_but_partial_publication_is_not(self):
        connection = Mock()
        connection.execute.return_value.fetchall.return_value = []
        _assert_group(connection, 'test', [('one', 'SELECT one', [(1,)])])
        connection.execute.return_value.fetchall.side_effect = [[], [(2,)]]
        with self.assertRaisesRegex(ValueError, 'test.one'):
            _assert_group(connection, 'test', [('one', 'SELECT one', [(1,)]), ('two', 'SELECT two', [(2,)])])


@unittest.skipUnless(os.environ.get('DATABASE_URL') or (Path(__file__).resolve().parents[1] / '.env').exists(),
                     'PostgreSQL integration requires DATABASE_URL or the local .env file')
class SeedGuardDatabaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.municipalities, cls.results, _ = replay_snapshot(ROOT / 'data/snapshot.json')
        cls.selected = read_snapshot()
        cls.assets = load_assets()

    def assert_compatible(self, connection):
        assert_seed_compatible(connection, self.municipalities, self.results, self.selected, self.assets)

    def test_matching_publication_guard_executes_selects_only(self):
        with connect() as connection:
            before = connection.execute('SELECT COUNT(*) FROM atlas.dataset_imports').fetchone()[0]
            observed = Mock(wraps=connection)
            self.assert_compatible(observed)
            self.assertTrue(observed.execute.call_args_list)
            self.assertTrue(all(call.args[0].lstrip().startswith('SELECT ') for call in observed.execute.call_args_list))
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM atlas.dataset_imports').fetchone()[0], before)

    def test_changed_value_and_additional_year_are_rejected_without_overwrite(self):
        with connect() as connection:
            connection.execute('SELECT pg_advisory_xact_lock(%s)', (PUBLICATION_LOCK,))
            for statement in [
                "UPDATE atlas.observations SET value=value+1 WHERE municipality_code='064033' AND indicator_id='births' AND period='2025'",
                "INSERT INTO atlas.observations SELECT municipality_code,indicator_id,'9999-test-only',value,status FROM atlas.observations WHERE municipality_code='064033' AND indicator_id='births' AND period='2025'",
            ]:
                with self.subTest(statement=statement), connection.transaction(force_rollback=True):
                    self.assertEqual(connection.execute(statement).rowcount, 1)
                    with self.assertRaisesRegex(ValueError, 'atlas.observations'):
                        self.assert_compatible(connection)
            self.assert_compatible(connection)


if __name__ == '__main__':
    unittest.main()
