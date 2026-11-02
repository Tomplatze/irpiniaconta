"""Publish verified source downloads and small documents without runtime filesystem reads."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

from psycopg.types.json import Jsonb

import psycopg

from etl.database import PUBLICATION_LOCK, record_import, require_current_schema, semantic_checksum, transaction

ROOT = Path(__file__).resolve().parent.parent
DOCUMENT_PATHS = {
    'collection-inventory': 'data/collection/inventory.json',
    'sections-map': 'data/sections-map.json',
    'editorial': 'config/editorial.json',
}


def load_assets(root: Path = ROOT) -> tuple[dict, dict]:
    """Verify every declared source/dictionary before opening a publication transaction."""
    documents = {key: json.loads((root / path).read_bytes()) for key, path in DOCUMENT_PATHS.items()}
    inventory = documents['collection-inventory']
    datasets = inventory.get('datasets')
    if inventory.get('schema_version') != 1 or not isinstance(datasets, list) or not isinstance(inventory.get('sources'), list):
        raise ValueError('Collection inventory schema invalid')
    if len(datasets) != inventory['summary']['collected_dataset_families']:
        raise ValueError('Collection inventory family count mismatch')
    identities = [dataset['id'] for dataset in datasets]
    if len(set(identities)) != len(identities) or any(not re.fullmatch(r'[a-z0-9_-]{1,100}', key) for key in identities):
        raise ValueError('Collection dataset identifiers invalid or duplicated')
    features = documents['sections-map'].get('features', [])
    codes = [feature.get('code', '') for feature in features]
    if len(set(codes)) != 118 or len(codes) != 118 or any(not re.fullmatch(r'064\d{3}', code) for code in codes):
        raise ValueError('Display map must contain 118 distinct municipal codes')
    selection = documents['editorial'].get('indicators')
    if not isinstance(selection, list) or not selection:
        raise ValueError('Editorial selection is missing')

    artifacts = {}
    collection_root = (root / 'data/collection').resolve()
    for dataset in datasets:
        declarations = [(dataset['staging_file'], dataset['staging_sha256'], 'source-rows')]
        declarations.extend((item['path'], item['sha256'], 'metadata') for item in dataset.get('metadata_files', []))
        for name, expected, kind in declarations:
            path = PurePosixPath(name)
            suffix = '.rows.jsonl.gz' if kind == 'source-rows' else '.json'
            if (str(path) != name or path.is_absolute() or path.parts[:2] != ('data', 'collection') or len(path.parts) != 3
                    or not re.fullmatch(r'[A-Za-z0-9_.-]+', path.name) or not path.name.endswith(suffix)):
                raise ValueError(f'Artifact path outside the collection: {name}')
            resolved = (root / path).resolve()
            if not resolved.is_relative_to(collection_root):
                raise ValueError(f'Artifact symlink outside the collection: {name}')
            payload = resolved.read_bytes()
            actual = hashlib.sha256(payload).hexdigest()
            if actual != expected:
                raise ValueError(f'Artifact checksum mismatch: {name}')
            if kind == 'metadata':
                json.loads(payload)
            if name in artifacts and artifacts[name]['sha256'] != actual:
                raise ValueError(f'Conflicting artifact declaration: {name}')
            artifacts[name] = {'payload': payload, 'sha256': actual, 'kind': kind}
    return documents, artifacts


def publish_assets(root: Path = ROOT, connection: psycopg.Connection | None = None, *, assets: tuple[dict, dict] | None = None) -> dict:
    """Replace validated assets transactionally; unchanged imports do not modify rows or traces."""
    documents, artifacts = assets if assets is not None else load_assets(root)
    checksum = semantic_checksum({
        'documents': documents,
        'artifacts': {name: {'sha256': row['sha256'], 'kind': row['kind']} for name, row in artifacts.items()},
    })
    with transaction(connection) as database:
        require_current_schema(database)
        database.execute('SELECT pg_advisory_xact_lock(%s)', (PUBLICATION_LOCK,))
        prior_documents = dict(database.execute('SELECT key, document FROM atlas.publication_documents').fetchall())
        prior_artifacts = {row[0]: (row[1], row[2]) for row in database.execute(
            'SELECT path, sha256, kind FROM atlas.publication_artifacts').fetchall()}
        retired = prior_artifacts.keys() - artifacts.keys()
        if retired:
            raise ValueError('Refusing asset publication: previously published downloads are missing from the new inventory. '
                             f'Retiring downloads requires review: {", ".join(sorted(retired))}')
        changed_documents = [(key, document) for key, document in documents.items() if prior_documents.get(key) != document]
        changed_artifacts = [(name, row) for name, row in artifacts.items()
                             if prior_artifacts.get(name) != (row['sha256'], row['kind'])]
        if not changed_documents and not changed_artifacts:
            return {'status': 'unchanged', 'documents': len(documents), 'artifacts': len(artifacts), 'checksum': checksum}
        with database.cursor() as cursor:
            cursor.executemany(
                'INSERT INTO atlas.publication_documents (key, document) VALUES (%s, %s) '
                'ON CONFLICT (key) DO UPDATE SET document = EXCLUDED.document',
                [(key, Jsonb(document)) for key, document in changed_documents],
            )
            cursor.executemany(
                'INSERT INTO atlas.publication_artifacts (path, payload, sha256, kind) VALUES (%s, %s, %s, %s) '
                'ON CONFLICT (path) DO UPDATE SET payload = EXCLUDED.payload, sha256 = EXCLUDED.sha256, kind = EXCLUDED.kind',
                [(name, row['payload'], row['sha256'], row['kind']) for name, row in changed_artifacts],
            )
        inserted = sum(key not in prior_documents for key, _ in changed_documents) + sum(name not in prior_artifacts for name, _ in changed_artifacts)
        updated = len(changed_documents) + len(changed_artifacts) - inserted
        record_import(database, dataset_key='publication-assets/bundle', source_name='Verified local publication assets',
                      source_version=documents['collection-inventory']['generated_at'], checksum=checksum, status='success',
                      records_processed=len(documents) + len(artifacts), records_inserted=inserted, records_updated=updated)
    return {'status': 'success', 'documents': len(documents), 'artifacts': len(artifacts),
            'inserted': inserted, 'updated': updated, 'checksum': checksum}


def main() -> None:
    """Import only locally verified artifacts; never acquire data or configure cloud services."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    print(json.dumps(publish_assets(), indent=2))


if __name__ == '__main__':
    main()
