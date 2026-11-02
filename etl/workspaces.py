"""Isolate prepared publications and preserve recoverable filesystem promotion."""
from __future__ import annotations

from contextlib import contextmanager, ExitStack
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
from typing import Iterator


def file_hash(path: Path) -> str:
    """Hash evidence without retaining entire files in memory."""
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def configuration_hash(root: Path) -> str:
    """Detect configuration changes between preparation and publication."""
    checksums = {path.name: file_hash(path) for path in sorted((root / 'config').glob('*.json'))}
    return hashlib.sha256(json.dumps(checksums, sort_keys=True).encode()).hexdigest()


def save_report(path: Path, report: dict) -> None:
    """Replace a run report atomically without exposing credentials."""
    temporary = path.with_suffix('.pending')
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    os.replace(temporary, path)


@contextmanager
def publication_files_lock(root: Path) -> Iterator[None]:
    """Exclude legacy writers as well as concurrent complete workflows."""
    names = ['data/refresh.lock', 'data/collection/collection.lock', 'data/sections.lock']
    with ExitStack() as stack:
        for name in names:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            handle = stack.enter_context(path.open('a'))
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise RuntimeError('Another data preparation or publication is running') from None
        yield


def run_path(root: Path, identity: str) -> Path:
    """Accept generated run identifiers only; never interpret user input as a path."""
    if not re.fullmatch(r'[a-f0-9]{32}', identity):
        raise ValueError('Invalid run identifier')
    return root / '.local/runs' / identity


def create_workspace(root: Path, directory: Path) -> Path:
    """Copy publication inputs only; raw acquisitions remain in their own shared cache."""
    workspace = directory / 'workspace'
    workspace.mkdir()
    shutil.copytree(root / 'config', workspace / 'config')
    (workspace / 'data').mkdir()
    for name in ['snapshot.json', 'snapshot.sha256', 'verification.json', 'sections.snapshot.json',
                 'sections.snapshot.sha256', 'sections-map.json']:
        source = root / 'data' / name
        if source.exists():
            shutil.copy2(source, workspace / 'data' / name)
    collection = root / 'data/collection'
    if collection.exists():
        shutil.copytree(collection, workspace / 'data/collection',
                        ignore=shutil.ignore_patterns('*.lock', '*.pending*', '.DS_Store'))
    else:
        (workspace / 'data/collection').mkdir()
    return workspace


def publication_files(workspace: Path) -> dict[str, str]:
    """Select normalized files for promotion, excluding raw data and build dependencies."""
    files = {}
    for path in (workspace / 'data').rglob('*'):
        if path.is_file() and not path.name.endswith('.lock') and '.pending' not in path.name:
            files[str(path.relative_to(workspace))] = file_hash(path)
    return files


def promote_files(workspace: Path, root: Path, files: dict[str, str]) -> None:
    """Promote prepared files atomically per file; an interrupted copy is safely repeatable."""
    for name, expected in sorted(files.items()):
        if not name.startswith('data/') or '..' in Path(name).parts:
            raise ValueError(f'Invalid publication path: {name}')
        source = workspace / name
        if source.is_symlink() or file_hash(source) != expected:
            raise ValueError(f'Prepared publication changed: {name}')
        destination = root / name
        if any(parent.is_symlink() for parent in [destination, *destination.parents] if parent.is_relative_to(root)):
            raise ValueError(f'Local publication symlink: {name}')
        if destination.is_file() and file_hash(destination) == expected:
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(destination.name + '.pending')
        shutil.copyfile(source, temporary)
        os.replace(temporary, destination)
