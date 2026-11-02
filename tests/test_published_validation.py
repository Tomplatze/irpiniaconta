"""Reject corrupt published data on PostgreSQL without committing any test changes."""
import os
import unittest

from psycopg.types.json import Jsonb

from etl.database import ROOT, connect
from etl.validate import validate_published
from test_database import fingerprints, rolled_back_connection


@unittest.skipUnless(os.environ.get('DATABASE_URL') or (ROOT / '.env').is_file(),
                     'Published validation requires the configured local PostgreSQL.')
class PublishedValidationTests(unittest.TestCase):
    def test_read_only_validation_reports_actual_counts_and_targeted_dataset(self):
        with connect() as database:
            database.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY')
            before = fingerprints(database, 'atlas'), fingerprints(database, 'sections')
            result = validate_published(database)
            self.assertEqual(result['core_observations'], database.execute('SELECT count(*) FROM atlas.observations').fetchone()[0])
            self.assertEqual(result['stored_metric_definitions'], database.execute('SELECT count(*) FROM sections.metrics').fetchone()[0])
            self.assertEqual(result['selected_metrics'], 46)
            self.assertEqual(result['supporting_historical_series'], 4)
            self.assertEqual(result['selected_metrics'] + result['supporting_historical_series'] + result['supporting_breakdown_series'], result['stored_metric_definitions'])
            self.assertEqual(result['verified_downloads'], database.execute('SELECT count(*) FROM atlas.publication_artifacts').fetchone()[0])
            self.assertEqual(validate_published(database, 'istat_balance')['datasets_checked'], 1)
            self.assertEqual((fingerprints(database, 'atlas'), fingerprints(database, 'sections')), before)

    def test_stored_core_values_are_checked_semantically(self):
        with rolled_back_connection() as database:
            identity = database.execute("SELECT id FROM atlas.indicators WHERE unit='%' ORDER BY position LIMIT 1").fetchone()[0]
            database.execute("UPDATE atlas.observations SET value=101 WHERE indicator_id=%s AND status='observed'", (identity,))
            with self.assertRaisesRegex(ValueError, 'Percentage exceeds 100'):
                validate_published(database)

    def test_missing_core_measurements_cannot_be_reported_as_valid(self):
        with rolled_back_connection() as database:
            database.execute('DELETE FROM atlas.observations')
            with self.assertRaisesRegex(ValueError, 'Ready dataset has no verified observations'):
                validate_published(database)

    def test_empty_selected_measurements_and_stale_latest_metadata_are_rejected(self):
        with rolled_back_connection() as database:
            with self.assertRaisesRegex(ValueError, 'metric periods'), database.transaction():
                database.execute('DELETE FROM sections.values_annual')
                validate_published(database)
            with self.assertRaisesRegex(ValueError, 'metric periods'), database.transaction():
                identity, metadata = database.execute('SELECT id,metadata FROM sections.metrics ORDER BY position LIMIT 1').fetchone()
                metadata['latest_period'] = 'synthetic-invalid-period'
                database.execute('UPDATE sections.metrics SET metadata=%s WHERE id=%s', (Jsonb(metadata), identity))
                validate_published(database)

    def test_modified_bytea_and_wrong_download_kind_are_rejected(self):
        with rolled_back_connection() as database:
            path = database.execute('SELECT path FROM atlas.publication_artifacts ORDER BY path LIMIT 1').fetchone()[0]
            for statement in [
                "UPDATE atlas.publication_artifacts SET payload=payload || decode('00','hex') WHERE path=%s",
                "UPDATE atlas.publication_artifacts SET kind='synthetic-invalid-kind' WHERE path=%s",
            ]:
                with self.subTest(statement=statement), self.assertRaisesRegex(ValueError, 'artifact checksum, length or kind'), database.transaction():
                    database.execute(statement, (path,))
                    validate_published(database)

    def test_download_allowlist_and_required_documents_are_enforced(self):
        with rolled_back_connection() as database:
            with self.assertRaisesRegex(ValueError, 'allowlist'), database.transaction():
                database.execute('DELETE FROM atlas.publication_artifacts WHERE path=(SELECT path FROM atlas.publication_artifacts LIMIT 1)')
                validate_published(database)
            with self.assertRaisesRegex(ValueError, 'documents are required'), database.transaction():
                database.execute("DELETE FROM atlas.publication_documents WHERE key='editorial'")
                validate_published(database)


if __name__ == '__main__':
    unittest.main()
