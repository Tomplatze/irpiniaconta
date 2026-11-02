"""Validate the single configuration boundary for source scope and refresh cadence."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_scope(root: Path = ROOT) -> dict[str, object]:
    """Fail early for duplicated IDs, category count drift or invalid source cadence."""
    scope = json.loads((root / 'config/sources.json').read_text())
    categories = scope['categories']
    sources = scope['sources']
    if len({row['id'] for row in sources}) != len(sources):
        raise ValueError('Duplicate source ID')
    for category in categories:
        if sum(row['category_id'] == category['id'] for row in sources) != category['expected_items']:
            raise ValueError(f"Scope count drift: {category['id']}")
    if any(row['category_id'] not in {c['id'] for c in categories} or row['cadence_days'] < 1 for row in sources):
        raise ValueError('Invalid source category or cadence')
    ordered_dependencies(sources)
    return scope


def ordered_dependencies(items: list[dict], selected: set[str] | None = None) -> list[dict]:
    """Validate and topologically order explicit dependencies, preserving authored order."""
    by_id = {item['id']: item for item in items}
    if len(by_id) != len(items):
        raise ValueError('Duplicate source or collection job ID')
    requested = set(by_id) if selected is None else selected
    if requested - by_id.keys():
        raise ValueError('Unknown source or collection job: ' + ', '.join(sorted(requested - by_id.keys())))
    ordered = []
    visiting = set()
    visited = set()

    def visit(identity: str) -> None:
        if identity not in by_id:
            raise ValueError(f'Unknown dependency: {identity}')
        if identity in visiting:
            raise ValueError(f'Cyclic dependency: {identity}')
        if identity in visited:
            return
        item = by_id[identity]
        if not isinstance(item.get('enabled', True), bool):
            raise ValueError(f'Invalid enabled flag: {identity}')
        dependencies = item.get('depends_on', [])
        if not isinstance(dependencies, list) or any(not isinstance(value, str) for value in dependencies):
            raise ValueError(f'Invalid dependency list: {identity}')
        visiting.add(identity)
        for dependency in dependencies:
            if item.get('enabled', True) and by_id.get(dependency, {}).get('enabled') is False:
                raise ValueError(f'Enabled source {identity} depends on disabled source {dependency}')
            visit(dependency)
        visiting.remove(identity)
        visited.add(identity)
        ordered.append(item)

    # Validate even unselected definitions before any network access or writes.
    for item in items:
        visit(item['id'])
    included = set()

    def include(identity: str) -> None:
        if identity in included:
            return
        included.add(identity)
        for dependency in by_id[identity].get('depends_on', []):
            include(dependency)

    for identity in requested:
        include(identity)
    return [item for item in ordered if item['id'] in included]


def load_collection(root: Path = ROOT) -> dict:
    """Validate collection definitions against the central source registry."""
    scope = load_scope(root)
    collection = json.loads((root / 'config/collection.json').read_text())
    known = {item['id'] for item in scope['sources']}
    ordered_dependencies(collection['jobs'])
    for job in collection['jobs']:
        if not set(job['scope_ids']) <= known:
            raise ValueError(f"Unknown scope for collection job: {job['id']}")
        for key in ['authority_crosswalk_job', 'project_crosswalk_job', 'building_crosswalk_job']:
            if job.get(key) and job[key] not in job.get('depends_on', []):
                raise ValueError(f"Undeclared {key} dependency: {job['id']}")
    return collection
