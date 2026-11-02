"""Semantic regression tests. Synthetic records are confined to test fixtures."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from etl.acquisition import Context
from etl.models import AdapterResult, Observation
from etl.pipeline import replay_snapshot, write_database, ROOT
from etl.quality import assess, validate_registry


class QualityTests(unittest.TestCase):
    """Test rejection rules rather than duplicating adapter transformations."""
    def setUp(self) -> None:
        self.metadata = {'id': 'test_only', 'status': 'ready', 'indicators': [
            {'id': 'count', 'label': 'Test', 'unit': 'persons', 'definition': 'Synthetic test only'},
            {'id': 'share', 'label': 'Test share', 'unit': '%', 'definition': 'Synthetic test only'},
            {'id': 'change', 'label': 'Test signed value', 'unit': 'ha', 'definition': 'Synthetic test only', 'allow_negative': True},
        ]}
        self.codes = {'064033', '064036'}

    def test_missing_suppressed_and_absent_are_distinct(self) -> None:
        result = AdapterResult(self.metadata, [Observation('064033', 'count', '2024', None, 'suppressed')])
        group = next(group for group in assess(result, self.codes)['groups'] if group['indicator_id'] == 'count')
        self.assertEqual((group['observed'], group['suppressed'], group['missing'], group['absent']), (0, 1, 0, 1))

    def test_zero_is_an_observation(self) -> None:
        result = AdapterResult(self.metadata, [Observation('064033', 'count', '2024', 0)])
        group = next(group for group in assess(result, self.codes)['groups'] if group['indicator_id'] == 'count')
        self.assertEqual(group['observed'], 1)

    def test_duplicate_is_rejected(self) -> None:
        item = Observation('064033', 'count', '2024', 1)
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            assess(AdapterResult(self.metadata, [item, item]), self.codes)

    def test_unknown_geography_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, 'Unreconciled'):
            assess(AdapterResult(self.metadata, [Observation('048017', 'count', '2024', 1)]), self.codes)

    def test_non_finite_is_rejected(self) -> None:
        for value in (float('nan'), float('inf')):
            with self.assertRaisesRegex(ValueError, 'finite'):
                assess(AdapterResult(self.metadata, [Observation('064033', 'count', '2024', value)]), self.codes)

    def test_null_observed_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, 'finite'):
            assess(AdapterResult(self.metadata, [Observation('064033', 'count', '2024', None)]), self.codes)

    def test_suppression_does_not_accept_zero(self) -> None:
        with self.assertRaisesRegex(ValueError, 'null'):
            assess(AdapterResult(self.metadata, [Observation('064033', 'count', '2024', 0, 'suppressed')]), self.codes)

    def test_invalid_percentage_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, '100'):
            assess(AdapterResult(self.metadata, [Observation('064033', 'share', '2024', 101)]), self.codes)

    def test_signed_soil_change_is_allowed(self) -> None:
        self.assertEqual(assess(AdapterResult(self.metadata, [Observation('064033', 'change', '2024', -1)]), self.codes)['rows'], 1)

    def test_negative_counts_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, 'Negative'):
            assess(AdapterResult(self.metadata, [Observation('064033', 'count', '2024', -1)]), self.codes)

    def test_period_coverage_is_not_combined(self) -> None:
        result = AdapterResult(self.metadata, [Observation('064033', 'count', '2023', 1), Observation('064036', 'count', '2024', 2)])
        groups = [group for group in assess(result, self.codes)['groups'] if group['indicator_id'] == 'count']
        self.assertEqual([group['observed'] for group in groups], [1, 1])
        self.assertEqual([group['absent'] for group in groups], [1, 1])

    def test_declared_indicator_with_no_records_is_visible(self) -> None:
        result = AdapterResult(self.metadata, [Observation('064033', 'count', '2024', 1)])
        groups = assess(result, self.codes)['groups']
        absent = next(group for group in groups if group['indicator_id'] == 'share')
        self.assertEqual((absent['observed'], absent['absent']), (0, 2))

    def test_blocked_source_cannot_publish_partial_values(self) -> None:
        metadata = {**self.metadata, 'status': 'blocked', 'blocker': 'Test fixture'}
        with self.assertRaisesRegex(ValueError, 'Blocked'):
            assess(AdapterResult(metadata, [Observation('064033', 'count', '2024', 1)]), self.codes)

    def test_offline_artifact_cannot_be_relabelled_as_a_different_url(self) -> None:
        import hashlib
        import json
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source.csv'
            path.write_bytes(b'test-only')
            proof = {'url': 'https://example.test/original', 'filename': 'source.csv', 'bytes': 9,
                     'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
            path.with_suffix('.csv.acquisition.json').write_text(json.dumps(proof))
            context = Context(Path(directory), offline=True)
            self.assertEqual(context.fetch('https://example.test/original', 'source.csv'), path)
            with self.assertRaisesRegex(RuntimeError, 'provenance'):
                context.fetch('https://example.test/changed', 'source.csv')
            with self.assertRaisesRegex(RuntimeError, 'provenance'):
                context.fetch('https://example.test/original', 'source.csv', method='POST', body={})


class SnapshotTests(unittest.TestCase):
    """Validate the actual acquired municipal snapshot and atomic database publication."""
    @classmethod
    def setUpClass(cls) -> None:
        cls.municipalities, cls.results, cls.report = replay_snapshot(ROOT / 'data/snapshot.json')

    def test_registry_has_exactly_118_reconciled_codes(self) -> None:
        self.assertEqual(len(validate_registry(self.municipalities)), 118)
        self.assertEqual(next(row['name'] for row in self.municipalities if row['code'] == '064033'), 'Fontanarosa')

    def test_all_registered_sources_are_explicit(self) -> None:
        self.assertEqual(len(self.results), 81)
        self.assertTrue(all(result.metadata['license_url'] or result.metadata['status'] == 'blocked' for result in self.results))
        for result in self.results:
            checks = assess(result, validate_registry(self.municipalities))
            if result.metadata['status'] == 'blocked':
                self.assertEqual(checks['rows'], 0)
                self.assertTrue(result.metadata['blocker'])
            else:
                self.assertGreater(checks['rows'] + checks['entities'], 0)
                self.assertTrue(result.metadata['artifacts'])

    def test_hash_tampering_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'snapshot.json'
            path.write_bytes((ROOT / 'data/snapshot.json').read_bytes() + b' ')
            path.with_suffix('.sha256').write_text((ROOT / 'data/snapshot.sha256').read_text())
            with self.assertRaisesRegex(RuntimeError, 'checksum'):
                replay_snapshot(path)

    def test_duplicate_snapshot_is_rejected_before_storage(self) -> None:
        invalid = deepcopy(self.results)
        ready = next(result for result in invalid if result.observations)
        ready.observations.append(ready.observations[0])
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            write_database(self.municipalities, invalid, self.report)

    def test_partial_registry_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, '118'):
            validate_registry(self.municipalities[:-1])


if __name__ == '__main__':
    unittest.main()
