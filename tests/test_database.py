"""Integration tests against the configured local PostgreSQL, with every data change rolled back."""
from contextlib import contextmanager
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import psycopg

from etl import database
from etl.database import ROOT, connect, load_core, load_sections, migrate, record_import, require_current_schema
from etl.migrate_sqlite import TABLES, copy_legacy, inspect_target, read_legacy, table_digest
from etl.pipeline import replay_snapshot
from etl.sections import read_snapshot


@contextmanager
def rolled_back_connection():
    """Exercise real transactions without changing the developer's publication."""
    connection = connect()
    try:
        require_current_schema(connection)
        yield connection
    finally:
        connection.rollback()
        connection.close()


def fingerprints(connection, schema: str) -> dict[str, str]:
    """Compare entire store contents before and after a failed publication."""
    return {table: table_digest(connection.execute(
        psycopg.sql.SQL('SELECT * FROM {}.{}').format(
            psycopg.sql.Identifier(schema), psycopg.sql.Identifier(table))).fetchall())
        for table in TABLES[schema]}


@unittest.skipUnless(os.environ.get('DATABASE_URL') or (ROOT / '.env').is_file(),
                     'Configure DATABASE_URL and run db:migrate for PostgreSQL integration tests.')
class PostgreSQLPublicationTests(unittest.TestCase):
    """Protect constraints, lossless conversion and transaction boundaries on the real engine."""

    @classmethod
    def setUpClass(cls):
        cls.municipalities, cls.results, cls.report = replay_snapshot(ROOT / 'data/snapshot.json')
        cls.sections = read_snapshot()

    def test_schema_migrations_are_repeatable(self):
        with rolled_back_connection() as connection:
            before = connection.execute('SELECT * FROM schema_migrations ORDER BY version').fetchall()
            self.assertEqual(migrate(connection), [])
            self.assertEqual(connection.execute('SELECT * FROM schema_migrations ORDER BY version').fetchall(), before)

    def test_edited_applied_migration_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory, rolled_back_connection() as connection:
            target = Path(directory)
            for path in database.MIGRATIONS.glob('*.sql'):
                (target / path.name).write_bytes(path.read_bytes())
            first = sorted(target.glob('*.sql'))[0]
            first.write_text(first.read_text() + '\n-- Changed applied migration fixture\n')
            with patch('etl.database.MIGRATIONS', target), self.assertRaisesRegex(RuntimeError, 'Applied migration changed'):
                migrate(connection)
            self.assertEqual(connection.execute('SELECT count(*) FROM atlas.municipalities').fetchone()[0], 118)

    def test_new_migrations_cannot_be_inserted_before_applied_versions(self):
        with tempfile.TemporaryDirectory() as directory, rolled_back_connection() as connection:
            target = Path(directory)
            for path in database.MIGRATIONS.glob('*.sql'):
                (target / path.name).write_bytes(path.read_bytes())
            (target / '000_out_of_order.sql').write_text('SELECT 1;')
            with patch('etl.database.MIGRATIONS', target), self.assertRaisesRegex(RuntimeError, 'higher version'):
                migrate(connection)

    def test_postgresql_enforces_geography_missingness_and_finite_values(self):
        with rolled_back_connection() as connection:
            indicator = connection.execute('SELECT id FROM atlas.indicators ORDER BY position LIMIT 1').fetchone()[0]
            for code, value, status, exception in [
                ('064999', 1, 'observed', psycopg.errors.ForeignKeyViolation),
                ('064033', 1, 'missing', psycopg.errors.CheckViolation),
                ('064033', float('nan'), 'observed', psycopg.errors.CheckViolation),
            ]:
                with self.assertRaises(exception), connection.transaction():
                    connection.execute('INSERT INTO atlas.observations VALUES (%s,%s,%s,%s,%s)',
                                       (code, indicator, 'transaction-test', value, status))
            with connection.transaction():
                connection.execute('INSERT INTO atlas.observations VALUES (%s,%s,%s,%s,%s)',
                                   ('064033', indicator, 'transaction-test', None, 'suppressed'))

    def test_bulk_core_failure_preserves_every_original_table(self):
        with rolled_back_connection() as connection:
            before = fingerprints(connection, 'atlas')
            original_copy = database.copy_rows

            def fail_observations(current, schema, table, columns, rows):
                if table == 'observations':
                    raise RuntimeError('Intentional bulk import failure')
                return original_copy(current, schema, table, columns, rows)

            with patch('etl.database.copy_rows', fail_observations), self.assertRaisesRegex(RuntimeError, 'Intentional bulk'):
                load_core(self.municipalities, self.results, self.report, connection=connection)
            self.assertEqual(fingerprints(connection, 'atlas'), before)

    def test_bulk_section_failure_preserves_every_original_table(self):
        with rolled_back_connection() as connection:
            before = fingerprints(connection, 'sections')
            original_copy = database.copy_rows

            def fail_monthly(current, schema, table, columns, rows):
                if table == 'values_monthly':
                    raise RuntimeError('Intentional monthly import failure')
                return original_copy(current, schema, table, columns, rows)

            with patch('etl.database.copy_rows', fail_monthly), self.assertRaisesRegex(RuntimeError, 'Intentional monthly'):
                load_sections(self.sections, connection=connection)
            self.assertEqual(fingerprints(connection, 'sections'), before)

    def test_reimport_is_idempotent_and_records_unchanged_datasets(self):
        with rolled_back_connection() as connection:
            for _ in range(2):
                load_core(self.municipalities, self.results, self.report, connection=connection)
                load_sections(self.sections, connection=connection)
            self.assertEqual(connection.execute('SELECT count(*) FROM atlas.observations').fetchone()[0], 37170)
            self.assertEqual(connection.execute('SELECT count(*) FROM sections.values_annual').fetchone()[0], sum(len(metric['cells']) for metric in self.sections['metrics']))
            row = connection.execute('''SELECT status,records_inserted,records_updated FROM atlas.dataset_imports
                WHERE dataset_key='sections.resident_population_history' ORDER BY id DESC LIMIT 1''').fetchone()
            self.assertEqual(row, ('unchanged', 0, 0))

    def test_import_timestamps_do_not_invent_a_source_publication_date(self):
        with rolled_back_connection() as connection:
            identity = record_import(connection, dataset_key='test.import-periods', source_name='Synthetic import fixture',
                                     reference_period='2020', checksum='0' * 64, status='success')
            period, published, imported, started, completed = connection.execute('''SELECT reference_period,published_at,imported_at,started_at,completed_at
                FROM atlas.dataset_imports WHERE id=%s''', (identity,)).fetchone()
            self.assertEqual(period, '2020')
            self.assertIsNone(published)
            self.assertIsNotNone(imported)
            self.assertGreaterEqual(completed, started)

    def test_legacy_values_and_authored_order_remain_lossless(self):
        with rolled_back_connection() as connection:
            for schema, path in [('atlas', ROOT / 'data/atlas.sqlite'), ('sections', ROOT / 'data/sections.sqlite')]:
                if not path.is_file():
                    self.skipTest('Retained original SQLite publication is not present in this checkout.')
                original = read_legacy(path, schema)
                # Rehearse the actual conversion inside an uncommitted transaction, regardless of later catalogue edits.
                connection.execute('SELECT pg_advisory_xact_lock(%s)', (database.PUBLICATION_LOCK,))
                for table in reversed(TABLES[schema]):
                    connection.execute(psycopg.sql.SQL('DELETE FROM {}.{}').format(
                        psycopg.sql.Identifier(schema), psycopg.sql.Identifier(table)))
                copy_legacy(connection, schema, original)
                comparison = inspect_target(connection, schema, original)
                self.assertTrue(all(row['matches'] for row in comparison.values()), comparison)


if __name__ == '__main__':
    unittest.main()
