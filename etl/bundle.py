"""Transfer a verified publication separately from Git, without touching PostgreSQL."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import tarfile
import tempfile

from etl.pipeline import replay_snapshot
from etl.publication_assets import load_assets
from etl.sections import read_snapshot

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'bundle-manifest.json'
MAX_BYTES = 1024 * 1024 * 1024
REQUIRED = {
    'data/snapshot.json', 'data/snapshot.sha256',
    'data/sections.snapshot.json', 'data/sections.snapshot.sha256',
    'data/sections-map.json', 'data/collection/inventory.json',
    'data/collection/manifest.json', 'data/collection/municipal-boundaries.geojson',
}
OPTIONAL = {
    'data/boundary-attributes-2026.csv', 'data/verification.json',
    'data/weather-verification.json', 'data/geography-verification.json',
}


def checksum(path: Path) -> str:
    """Hash bytes without loading national datasets into memory."""
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def configuration(root: Path) -> dict[str, str]:
    """Bind the bundle to the versioned dataset and presentation contracts."""
    return {str(path.relative_to(root)): checksum(path) for path in sorted((root / 'config').glob('*.json'))}


def safe_path(root: Path, name: str) -> Path:
    """Accept canonical data paths only and reject symlinks, including parents."""
    path = PurePosixPath(name)
    if (str(path) != name or len(path.parts) < 2 or path.parts[0] != 'data'
            or any(not re.fullmatch(r'[A-Za-z0-9_.-]+', part) or part in {'.', '..'} for part in path.parts[1:])):
        raise ValueError(f'Invalid bundle path: {name}')
    target = root / path
    if any((root.joinpath(*path.parts[:depth])).is_symlink() for depth in range(1, len(path.parts) + 1)):
        raise ValueError(f'Symlink in bundle path: {name}')
    if target.exists() and not target.is_file():
        raise ValueError(f'Bundle target is not a regular file: {name}')
    return target


def publication_files(root: Path) -> set[str]:
    """Validate seed inputs and select only evidence required for publication replay."""
    municipalities, _, _ = replay_snapshot(root / 'data/snapshot.json')
    selected = read_snapshot(root / 'data/sections.snapshot.json')
    documents, artifacts = load_assets(root)
    if municipalities != selected['municipalities']:
        raise ValueError('Publication municipal registries disagree')
    lineage = selected['lineage']
    for key, name in [('product_snapshot_sha256', 'data/snapshot.json'),
                      ('collection_inventory_sha256', 'data/collection/inventory.json'),
                      ('configuration_sha256', 'config/sections.json')]:
        if lineage[key] != checksum(root / name):
            raise ValueError(f'Publication lineage mismatch: {name}')
    files = REQUIRED | set(artifacts) | {name for name in OPTIONAL if (root / name).is_file()}
    crest_manifest_path = root / 'data/municipal-crests/manifest.json'
    if crest_manifest_path.is_file():
        crest_manifest = json.loads(crest_manifest_path.read_text())
        registry = {row['code']: row['name'] for row in municipalities}
        records = crest_manifest['records']
        if len(records) != len(registry) or {row['code']: row['name'] for row in records} != registry:
            raise ValueError('Municipal crest registry does not match the publication')
        files.add('data/municipal-crests/manifest.json')
        for record in records:
            if not record.get('file'):
                continue
            filename = record.get('filename', '')
            if not re.fullmatch(rf"{record['code']}\.(?:jpg|png|gif|webp)", filename) or record['file'] != f"/api/municipal-crests/{record['code']}":
                raise ValueError('Invalid municipal crest filename or route')
            name = f'data/municipal-crests/{filename}'
            if checksum(safe_path(root, name)) != record.get('sha256'):
                raise ValueError(f'Municipal crest checksum mismatch: {record["code"]}')
            files.add(name)
    for snapshot in sorted((root / 'data/history').glob('*/snapshot.json')):
        replay_snapshot(snapshot)
        files.update(str(path.relative_to(root)) for path in
                     [snapshot, snapshot.with_suffix('.sha256'), snapshot.with_name('report.json')])
    for name in files:
        if not safe_path(root, name).is_file():
            raise ValueError(f'Missing publication input: {name}')
    if not documents['collection-inventory']['datasets']:
        raise ValueError('Cannot transfer an empty collection')
    return files


def pack(root: Path, destination: Path) -> dict:
    """Validate and export local evidence, refusing to replace an existing archive."""
    files = publication_files(root)
    records = {name: {'sha256': checksum(root / name), 'bytes': (root / name).stat().st_size}
               for name in sorted(files)}
    manifest = {'schema_version': 1, 'configuration': configuration(root), 'files': records}
    encoded = (json.dumps(manifest, indent=2) + '\n').encode()
    sidecar = destination.with_name(destination.name + '.sha256')
    if destination.exists() or sidecar.exists():
        raise ValueError('Bundle destination already exists; choose a new archive path')
    with destination.open('xb') as output:
        try:
            with tarfile.open(fileobj=output, mode='w:gz') as archive:
                header = tarfile.TarInfo(MANIFEST)
                header.size = len(encoded)
                archive.addfile(header, io.BytesIO(encoded))
                for name in sorted(files):
                    payload = (root / name).read_bytes()
                    if hashlib.sha256(payload).hexdigest() != records[name]['sha256']:
                        raise ValueError('Publication changed during export; retry with ingestion stopped')
                    header = tarfile.TarInfo(name)
                    header.size = len(payload)
                    header.mode = 0o600
                    archive.addfile(header, io.BytesIO(payload))
        except BaseException:
            destination.unlink(missing_ok=True)
            raise
    sidecar.write_text(f'{checksum(destination)}  {destination.name}\n')
    return {'status': 'packed', 'files': len(files), 'archive_bytes': destination.stat().st_size,
            'archive': str(destination), 'sha256': checksum(destination)}


def unpack(root: Path, source: Path) -> dict:
    """Verify the entire archive before adding missing files; never overwrite local evidence."""
    expected = source.with_name(source.name + '.sha256').read_text().split()[0]
    if not re.fullmatch(r'[a-f0-9]{64}', expected) or checksum(source) != expected:
        raise ValueError('Bundle archive checksum mismatch')
    with tempfile.TemporaryDirectory(prefix='irpiniaconta-bundle-') as directory:
        staging = Path(directory)
        with tarfile.open(source, 'r:gz') as archive:
            members = archive.getmembers()
            names = [member.name for member in members]
            if (len(members) > 10000 or len(set(names)) != len(names)
                    or any(not member.isfile() or member.size < 0 for member in members)
                    or sum(member.size for member in members) > MAX_BYTES):
                raise ValueError('Bundle has duplicate, oversized or non-file entries')
            if MANIFEST not in names or archive.getmember(MANIFEST).size > 1024 * 1024:
                raise ValueError('Bundle manifest is missing or oversized')
            manifest = json.load(archive.extractfile(MANIFEST))
            if manifest['schema_version'] != 1 or manifest['configuration'] != configuration(root):
                raise ValueError('Bundle configuration differs from this checkout')
            if set(names) != set(manifest['files']) | {MANIFEST}:
                raise ValueError('Bundle file list differs from its manifest')
            for name, record in manifest['files'].items():
                target = safe_path(staging, name)
                if archive.getmember(name).size != record['bytes']:
                    raise ValueError(f'Bundle file size mismatch: {name}')
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.extractfile(name) as payload, target.open('xb') as output:
                    shutil.copyfileobj(payload, output)
                if checksum(target) != record['sha256']:
                    raise ValueError(f'Bundle file checksum mismatch: {name}')
        shutil.copytree(root / 'config', staging / 'config')
        if publication_files(staging) != set(manifest['files']):
            raise ValueError('Bundle contains missing or unrelated publication files')
        missing = []
        for name, record in manifest['files'].items():
            target = safe_path(root, name)
            if target.exists():
                if checksum(target) != record['sha256']:
                    raise ValueError(f'Refusing to overwrite different local evidence: {name}')
            else:
                missing.append((name, target))
        created = []
        try:
            for name, target in missing:
                safe_path(root, name)
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open('xb') as output:
                    created.append(target)
                    with (staging / name).open('rb') as payload:
                        shutil.copyfileobj(payload, output)
        except BaseException:
            for target in reversed(created):
                target.unlink(missing_ok=True)
            raise
    return {'status': 'unpacked', 'files': len(manifest['files']), 'created': len(created)}


def main() -> None:
    """Expose explicit filesystem-only export and import operations."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['pack', 'unpack'])
    parser.add_argument('archive', type=Path)
    arguments = parser.parse_args()
    try:
        result = (pack if arguments.operation == 'pack' else unpack)(ROOT, arguments.archive.resolve())
    except (OSError, ValueError, KeyError, tarfile.TarError) as error:
        parser.exit(1, f'Bundle failed: {error}\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
