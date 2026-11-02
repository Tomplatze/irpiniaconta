"""Protect immutable source downloads and transactional PostgreSQL asset publication."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from etl.publication_assets import load_assets, publish_assets
from etl.database import connect


def write_fixture(root: Path, *, checksum: str | None = None, staging_path: str = 'data/collection/test.rows.jsonl.gz') -> None:
    """Create explicitly synthetic source evidence for validation-failure tests."""
    (root / 'data/collection').mkdir(parents=True)
    (root / 'config').mkdir()
    payload = gzip.compress(b'{"source":{"value":"test-only"}}\n')
    (root / 'data/collection/test.rows.jsonl.gz').write_bytes(payload)
    dictionary = b'{ "definition": "synthetic test only" }\n'
    (root / 'data/collection/test.dictionary.json').write_bytes(dictionary)
    inventory = {'schema_version': 1, 'generated_at': '2026-10-16T00:00:00Z', 'sources': [],
                 'summary': {'collected_dataset_families': 1}, 'datasets': [{
                     'id': 'test', 'staging_file': staging_path,
                     'staging_sha256': checksum or hashlib.sha256(payload).hexdigest(),
                     'metadata_files': [{'path': 'data/collection/test.dictionary.json',
                                         'sha256': hashlib.sha256(dictionary).hexdigest()}],
                 }]}
    (root / 'data/collection/inventory.json').write_text(json.dumps(inventory))
    (root / 'data/sections-map.json').write_text(json.dumps({'features': [{'code': f'064{index:03}'} for index in range(1, 119)]}))
    (root / 'config/editorial.json').write_text(json.dumps({'indicators': [{'id': 'test-only'}]}))


class PublicationAssetValidationTests(unittest.TestCase):
    def test_source_download_and_dictionary_bytes_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_fixture(root)
            documents, artifacts = load_assets(root)
            self.assertEqual(set(documents), {'collection-inventory', 'sections-map', 'editorial'})
            for name, artifact in artifacts.items():
                self.assertEqual(artifact['payload'], (root / name).read_bytes())
            self.assertEqual(artifacts['data/collection/test.dictionary.json']['payload'], b'{ "definition": "synthetic test only" }\n')

    def test_bad_checksum_and_paths_are_rejected_before_import(self):
        for options in ({'checksum': '0' * 64}, {'staging_path': 'data/collection/../../README.md'}):
            with self.subTest(options=options), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                write_fixture(root, **options)
                with self.assertRaisesRegex(ValueError, 'checksum|outside'):
                    load_assets(root)


@unittest.skipUnless(os.environ.get('DATABASE_URL') or (Path(__file__).resolve().parents[1] / '.env').exists(),
                     'PostgreSQL integration requires DATABASE_URL or the local .env file')
class PublicationAssetDatabaseTests(unittest.TestCase):
    def test_real_bundle_is_idempotent_and_invalid_import_preserves_publication(self):
        publish_assets()
        _, original_artifacts = load_assets()
        with connect() as connection:
            before_documents = connection.execute('SELECT key, document FROM atlas.publication_documents ORDER BY key').fetchall()
            before_artifacts = connection.execute(
                'SELECT path, sha256, octet_length(payload), kind FROM atlas.publication_artifacts ORDER BY path').fetchall()
            before_runs = connection.execute("SELECT COUNT(*) FROM atlas.dataset_imports WHERE dataset_key = 'publication-assets/bundle'").fetchone()[0]
            for name, payload, checksum in connection.execute('SELECT path, payload, sha256 FROM atlas.publication_artifacts'):
                if name in original_artifacts:
                    self.assertEqual(payload, original_artifacts[name]['payload'])
                    self.assertEqual(hashlib.sha256(payload).hexdigest(), checksum)
        self.assertEqual(publish_assets()['status'], 'unchanged')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_fixture(root, checksum='0' * 64)
            with self.assertRaisesRegex(ValueError, 'checksum'):
                publish_assets(root)
        with connect() as connection:
            self.assertEqual(connection.execute('SELECT key, document FROM atlas.publication_documents ORDER BY key').fetchall(), before_documents)
            self.assertEqual(connection.execute(
                'SELECT path, sha256, octet_length(payload), kind FROM atlas.publication_artifacts ORDER BY path').fetchall(), before_artifacts)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM atlas.dataset_imports WHERE dataset_key = 'publication-assets/bundle'").fetchone()[0], before_runs)

    def test_caller_transaction_rollback_preserves_documents_and_import_trace(self):
        documents, artifacts = load_assets()
        documents['editorial']['principle'] = 'Synthetic rollback test only'
        with connect() as connection:
            previous = connection.execute("SELECT document FROM atlas.publication_documents WHERE key = 'editorial'").fetchone()
            before_runs = connection.execute("SELECT COUNT(*) FROM atlas.dataset_imports WHERE dataset_key = 'publication-assets/bundle'").fetchone()[0]
            with self.assertRaisesRegex(RuntimeError, 'Synthetic downstream failure'):
                with connection.transaction():
                    result = publish_assets(connection=connection, assets=(documents, artifacts))
                    self.assertEqual(result['status'], 'success')
                    raise RuntimeError('Synthetic downstream failure')
            self.assertEqual(connection.execute("SELECT document FROM atlas.publication_documents WHERE key = 'editorial'").fetchone(), previous)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM atlas.dataset_imports WHERE dataset_key = 'publication-assets/bundle'").fetchone()[0], before_runs)

    def test_retiring_a_download_rejects_changed_inventory_and_preserves_bytes_and_trace(self):
        documents, artifacts = load_assets()
        inventory = documents['collection-inventory']
        dataset = next(row for row in inventory['datasets'] if not row.get('metadata_files'))
        removed_path = dataset['staging_file']
        removed = artifacts.pop(removed_path)
        inventory['datasets'].remove(dataset)
        inventory['summary']['collected_dataset_families'] -= 1
        with connect() as connection:
            before_documents = connection.execute('SELECT key, document FROM atlas.publication_documents ORDER BY key').fetchall()
            before_runs = connection.execute("SELECT COUNT(*) FROM atlas.dataset_imports WHERE dataset_key = 'publication-assets/bundle'").fetchone()[0]
            with self.assertRaisesRegex(ValueError, 'Retiring downloads requires review'):
                publish_assets(connection=connection, assets=(documents, artifacts))
            self.assertEqual(connection.execute('SELECT key, document FROM atlas.publication_documents ORDER BY key').fetchall(), before_documents)
            self.assertEqual(connection.execute('SELECT payload, sha256, kind FROM atlas.publication_artifacts WHERE path = %s',
                                                (removed_path,)).fetchone(), (removed['payload'], removed['sha256'], removed['kind']))
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM atlas.dataset_imports WHERE dataset_key = 'publication-assets/bundle'").fetchone()[0], before_runs)


if __name__ == '__main__':
    unittest.main()
