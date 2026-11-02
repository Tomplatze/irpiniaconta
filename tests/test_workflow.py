"""Regression checks for dependency planning, isolated preparation and atomic publication."""
from contextlib import contextmanager
from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import uuid

from etl.database import connect, record_import, require_current_schema
from etl.publication import load_prepared, publish_prepared, revision
from etl.registry import ordered_dependencies
from etl import workflow
from etl.workspaces import publication_files_lock, run_path, save_report
from etl.models import AdapterResult
from etl.pipeline import replay_snapshot
from etl.registry import load_scope
from etl.refresh import prepare as prepare_core

ROOT = Path(__file__).resolve().parents[1]


class DependencyTests(unittest.TestCase):
    def test_dependency_closure_preserves_order_and_deduplicates_shared_inputs(self):
        definitions = [{'id': 'report', 'depends_on': ['registry', 'statistics']},
                       {'id': 'unrelated'}, {'id': 'statistics', 'depends_on': ['registry']}, {'id': 'registry'}]
        self.assertEqual([item['id'] for item in ordered_dependencies(definitions, {'report'})],
                         ['registry', 'statistics', 'report'])

    def test_cycles_unknown_dependencies_duplicates_and_disabled_inputs_fail_early(self):
        for definitions in [
            [{'id': 'a', 'depends_on': ['b']}, {'id': 'b', 'depends_on': ['a']}],
            [{'id': 'a', 'depends_on': ['missing']}], [{'id': 'a'}, {'id': 'a'}],
            [{'id': 'a', 'depends_on': ['b']}, {'id': 'b', 'enabled': False}],
        ]:
            with self.subTest(definitions=definitions), self.assertRaises(ValueError):
                ordered_dependencies(definitions)

    def test_real_plans_include_source_and_geographic_crosswalk_dependencies(self):
        school = workflow.plan(sources={'SER-03'})
        self.assertEqual(school['sources'], ['SER-01', 'SER-03'])
        all_jobs = workflow.plan()['jobs']
        for dependent in ['pnrr-projects-20260613', 'pnrr-procurements-20260613']:
            self.assertLess(all_jobs.index('pnrr-localizations-20260613'), all_jobs.index(dependent))

    def test_unknown_selection_is_rejected_without_a_database_connection(self):
        with patch('etl.workflow.baseline') as database, self.assertRaises(ValueError):
            workflow.plan(sources={'missing'})
        database.assert_not_called()

    def test_overlapping_workflows_and_legacy_refreshes_are_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with publication_files_lock(root):
                with self.assertRaisesRegex(RuntimeError, 'Another data'):
                    with publication_files_lock(root):
                        self.fail('Concurrent writer acquired the file locks')

    def test_disabling_a_source_preserves_its_last_valid_data_without_running_its_adapter(self):
        scope = load_scope()
        next(source for source in scope['sources'] if source['id'] == 'DEM-02')['enabled'] = False
        municipalities, original, _ = replay_snapshot(ROOT / 'data/snapshot.json')
        expected = next(dataset for dataset in original if dataset.metadata['source_id'] == 'DEM-02')
        with patch('etl.refresh.load_scope', return_value=scope), \
                patch('etl.adapters.registry.run', return_value=AdapterResult({}, municipalities=municipalities)), \
                patch('etl.refresh.run_adapter') as adapter:
            _, datasets, report = prepare_core(offline=True, source_ids=['DEM-02'], probe=False)
        actual = next(dataset for dataset in datasets if dataset.metadata['source_id'] == 'DEM-02')
        self.assertEqual(actual.observations, expected.observations)
        self.assertEqual(actual.metadata['artifacts'], expected.metadata['artifacts'])
        self.assertEqual(report['attempts'], [])
        adapter.assert_not_called()


class WorkflowRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.identity = uuid.uuid4().hex
        self.run = run_path(self.root, self.identity)
        (self.run / 'workspace').mkdir(parents=True)
        self.report = {'run_id': self.identity, 'status': 'prepared', 'plan': {'configuration_sha256': 'config'},
                       'files': {'data/snapshot.json': 'digest'}, 'checksum': 'bundle', 'expected_revision': [0, 0]}
        save_report(self.run / 'run.json', self.report)

    def test_interrupted_filesystem_promotion_can_resume_an_already_committed_run(self):
        with patch('etl.workflow.configuration_hash', return_value='config'), \
                patch('etl.workflow.publication_files', return_value=self.report['files']), \
                patch('etl.workflow.load_prepared'), \
                patch('etl.workflow.publish_prepared', side_effect=[{'status': 'committed'}, {'status': 'already_committed'}]), \
                patch('etl.workflow.promote_files', side_effect=[OSError('Synthetic disk interruption'), None]):
            with self.assertRaisesRegex(OSError, 'interruption'):
                workflow.publish(self.root, self.identity)
            self.assertEqual(json.loads((self.run / 'run.json').read_text())['status'], 'database_committed')
            self.assertTrue((self.run / 'workspace').exists())
            self.assertEqual(workflow.publish(self.root, self.identity)['status'], 'published')
        self.assertFalse((self.run / 'workspace').exists())
        self.assertEqual(workflow.publish(self.root, self.identity)['status'], 'published')

    def test_changed_configuration_or_staging_is_rejected_before_publication(self):
        with patch('etl.workflow.configuration_hash', return_value='changed'), \
                patch('etl.workflow.publish_prepared') as writer, self.assertRaisesRegex(ValueError, 'Configuration changed'):
            workflow.publish(self.root, self.identity)
        writer.assert_not_called()
        with patch('etl.workflow.configuration_hash', return_value='config'), \
                patch('etl.workflow.publication_files', return_value={}), \
                patch('etl.workflow.publish_prepared') as writer, self.assertRaisesRegex(ValueError, 'files changed'):
            workflow.publish(self.root, self.identity)
        writer.assert_not_called()

    def test_preparation_failure_preserves_a_report_and_never_calls_the_publisher(self):
        with patch('etl.workflow.plan', return_value={'sources': ['DEM-02'], 'jobs': [], 'configuration_sha256': 'config'}), \
                patch('etl.workflow.load_collection', return_value={'jobs': []}), \
                patch('etl.workflow.baseline', return_value=[0, 0]), \
                patch('etl.workflow.create_workspace', side_effect=ValueError('Synthetic preparation error')), \
                patch('etl.workflow.publish_prepared') as writer, self.assertRaisesRegex(ValueError, 'preparation error'):
            workflow.prepare(self.root)
        writer.assert_not_called()
        reports = [json.loads(path.read_text()) for path in (self.root / '.local/runs').glob('*/run.json')]
        self.assertTrue(any(report['status'] == 'failed' and 'preparation error' in report['error'] for report in reports))


@contextmanager
def rollback_connection():
    """Exercise actual PostgreSQL while keeping every test write uncommitted."""
    connection = connect()
    try:
        require_current_schema(connection)
        yield connection
    finally:
        connection.rollback()
        connection.close()


def publication_state(connection) -> list:
    """Fingerprint values, metadata, evidence and import/run ledgers across all publication layers."""
    tables = ['atlas.observations', 'atlas.datasets', 'sections.metrics', 'sections.values_annual',
              'sections.values_monthly', 'atlas.publication_documents', 'atlas.dataset_imports', 'atlas.ingestion_runs']
    return [connection.execute(f"SELECT md5(COALESCE(string_agg(t::text,'' ORDER BY t::text),'')) FROM {table} t").fetchone()
            for table in tables] + [connection.execute(
                'SELECT path,sha256,octet_length(payload) FROM atlas.publication_artifacts ORDER BY path').fetchall()]


@unittest.skipUnless(os.environ.get('DATABASE_URL') or (ROOT / '.env').exists(), 'Local PostgreSQL is required')
class AtomicPublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prepared = load_prepared(ROOT)

    def test_failure_after_asset_publication_rolls_back_all_layers_and_traces(self):
        prepared = deepcopy(self.prepared)
        prepared.datasets[0].metadata['name'] = 'Synthetic atomic rollback test'
        prepared.selected['metrics'][0]['label'] = 'Synthetic atomic rollback test'
        prepared.assets[0]['editorial']['principle'] = 'Synthetic atomic rollback test'
        with rollback_connection() as connection:
            before = publication_state(connection)
            expected = revision(connection)
            with patch('etl.publication.record_import', side_effect=RuntimeError('Synthetic failure after assets')), \
                    self.assertRaisesRegex(RuntimeError, 'after assets'):
                publish_prepared(prepared, identity=uuid.uuid4().hex, checksum='a' * 64, expected_revision=expected,
                                 connection=connection)
            self.assertEqual(publication_state(connection), before)

    def test_intervening_import_rejects_stale_preparation(self):
        with rollback_connection() as connection:
            expected = revision(connection)
            record_import(connection, dataset_key='test/concurrent', source_name='Synthetic concurrency fixture',
                          checksum='0' * 64, status='success')
            before = publication_state(connection)
            with self.assertRaisesRegex(ValueError, 'Database changed'):
                publish_prepared(self.prepared, identity=uuid.uuid4().hex, checksum='a' * 64,
                                 expected_revision=expected, connection=connection)
            self.assertEqual(publication_state(connection), before)

    def test_committed_run_marker_prevents_duplicate_imports_on_retry(self):
        with rollback_connection() as connection:
            identity = uuid.uuid4().hex
            expected = revision(connection)
            publish_prepared(self.prepared, identity=identity, checksum='a' * 64, expected_revision=expected, connection=connection)
            after = revision(connection)
            result = publish_prepared(self.prepared, identity=identity, checksum='a' * 64, expected_revision=expected,
                                      connection=connection)
            self.assertEqual(result['status'], 'already_committed')
            self.assertEqual(revision(connection), after)

    def test_recovery_cannot_promote_an_older_revision_over_a_newer_import(self):
        with rollback_connection() as connection:
            identity = uuid.uuid4().hex
            expected = revision(connection)
            publish_prepared(self.prepared, identity=identity, checksum='a' * 64,
                             expected_revision=expected, connection=connection)
            record_import(connection, dataset_key='test/newer', source_name='Synthetic later import',
                          checksum='0' * 64, status='success')
            with self.assertRaisesRegex(ValueError, 'newer import'):
                publish_prepared(self.prepared, identity=identity, checksum='a' * 64,
                                 expected_revision=expected, connection=connection)


if __name__ == '__main__':
    unittest.main()
