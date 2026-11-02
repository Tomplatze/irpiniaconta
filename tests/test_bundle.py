"""Protect separate data transfers against corruption and local evidence replacement."""
from pathlib import Path
import gzip
import hashlib
import io
import json
import shutil
import tarfile
import tempfile
import unittest

from etl.bundle import MANIFEST, checksum, pack, unpack


def fixture(root: Path) -> None:
    """Create synthetic transfer inputs used only by archive regression tests."""
    (root / 'config').mkdir()
    (root / 'data/collection').mkdir(parents=True)
    registry = [{'code': f'064{index:03}', 'name': str(index)} for index in range(1, 119)]
    payload = gzip.compress(b'{"fixture":true}\n')
    staging = 'data/collection/test.rows.jsonl.gz'
    (root / staging).write_bytes(payload)
    documents = {
        'config/editorial.json': {'indicators': ['fixture']},
        'config/sections.json': {'fixture': True},
        'data/snapshot.json': {'municipalities': registry, 'datasets': [], 'report': {}},
        'data/sections-map.json': {'features': [{'code': row['code']} for row in registry]},
        'data/collection/inventory.json': {'schema_version': 1, 'sources': [],
            'summary': {'collected_dataset_families': 1},
            'datasets': [{'id': 'test', 'staging_file': staging,
                          'staging_sha256': hashlib.sha256(payload).hexdigest(), 'metadata_files': []}]},
        'data/collection/manifest.json': {'fixture': True},
        'data/collection/municipal-boundaries.geojson': {'type': 'FeatureCollection', 'features': []},
    }
    for name, document in documents.items():
        (root / name).write_text(json.dumps(document))
    lineage = {key: checksum(root / name) for key, name in [
        ('product_snapshot_sha256', 'data/snapshot.json'),
        ('collection_inventory_sha256', 'data/collection/inventory.json'),
        ('configuration_sha256', 'config/sections.json')]}
    (root / 'data/sections.snapshot.json').write_text(json.dumps(
        {'municipalities': registry, 'metrics': [], 'lineage': lineage}))
    for name in ['snapshot', 'sections.snapshot']:
        (root / f'data/{name}.sha256').write_text(checksum(root / f'data/{name}.json') + '\n')


class BundleTests(unittest.TestCase):
    """Exercise real tar files and checksums without a database or network."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / 'original'
        self.root.mkdir()
        fixture(self.root)
        self.archive = Path(self.directory.name) / 'publication.tar.gz'
        pack(self.root, self.archive)
        self.target = Path(self.directory.name) / 'checkout'
        self.target.mkdir()
        shutil.copytree(self.root / 'config', self.target / 'config')

    def rewrite(self, transform) -> None:
        """Update outer integrity to exercise inner validation of untrusted tar entries."""
        with tarfile.open(self.archive, 'r:gz') as archive:
            entries = [(item, archive.extractfile(item).read()) for item in archive.getmembers()]
        with tarfile.open(self.archive, 'w:gz') as archive:
            for item, payload in transform(entries):
                item.size = len(payload)
                archive.addfile(item, io.BytesIO(payload))
        self.archive.with_name(self.archive.name + '.sha256').write_text(checksum(self.archive))

    def test_roundtrip_is_complete_and_repeated_import_is_unchanged(self):
        result = unpack(self.target, self.archive)
        self.assertEqual(result['files'], result['created'])
        for source in (self.root / 'data').rglob('*'):
            if source.is_file():
                self.assertEqual(source.read_bytes(), (self.target / source.relative_to(self.root)).read_bytes())
        self.assertEqual(unpack(self.target, self.archive)['created'], 0)

    def test_differing_evidence_is_preserved_before_any_file_is_added(self):
        (self.target / 'data').mkdir()
        path = self.target / 'data/snapshot.json'
        path.write_bytes(b'Existing local evidence')
        with self.assertRaisesRegex(ValueError, 'overwrite different'):
            unpack(self.target, self.archive)
        self.assertEqual(path.read_bytes(), b'Existing local evidence')
        self.assertEqual(list((self.target / 'data').iterdir()), [path])

    def test_corrupt_outer_archive_is_rejected_without_writes(self):
        with self.archive.open('ab') as output:
            output.write(b'corruption')
        with self.assertRaisesRegex(ValueError, 'archive checksum'):
            unpack(self.target, self.archive)
        self.assertFalse((self.target / 'data').exists())

    def test_corrupt_inner_file_is_rejected_without_writes(self):
        self.rewrite(lambda entries: [(item, b'!' * len(payload) if item.name.endswith('snapshot.json') else payload)
                                      for item, payload in entries])
        with self.assertRaisesRegex(ValueError, 'file checksum'):
            unpack(self.target, self.archive)
        self.assertFalse((self.target / 'data').exists())

    def test_changed_configuration_is_rejected_without_writes(self):
        (self.target / 'config/sections.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'configuration differs'):
            unpack(self.target, self.archive)
        self.assertFalse((self.target / 'data').exists())

    def test_path_traversal_is_rejected_even_with_matching_outer_hash(self):
        def traversal(entries):
            manifest = json.loads(entries[0][1])
            original = next(iter(manifest['files']))
            manifest['files']['data/../../escaped.json'] = manifest['files'].pop(original)
            for item, payload in entries:
                if item.name == original:
                    item.name = 'data/../../escaped.json'
                yield item, json.dumps(manifest).encode() if item.name == MANIFEST else payload
        self.rewrite(traversal)
        with self.assertRaisesRegex(ValueError, 'Invalid bundle path'):
            unpack(self.target, self.archive)
        self.assertFalse((self.target / 'data').exists())

    def test_symlinked_workspace_is_rejected_without_writes(self):
        outside = Path(self.directory.name) / 'outside'
        outside.mkdir()
        (self.target / 'data').symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            unpack(self.target, self.archive)
        self.assertEqual(list(outside.iterdir()), [])

    def test_duplicate_tar_entries_are_rejected(self):
        self.rewrite(lambda entries: [*entries, entries[-1]])
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            unpack(self.target, self.archive)

    def test_existing_export_is_never_overwritten(self):
        previous = checksum(self.archive)
        with self.assertRaisesRegex(ValueError, 'already exists'):
            pack(self.root, self.archive)
        self.assertEqual(checksum(self.archive), previous)


if __name__ == '__main__':
    unittest.main()
