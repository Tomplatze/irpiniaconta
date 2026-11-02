"""Coverage and semantic checks independent of adapter implementation."""
from collections import defaultdict
from math import isfinite
from etl.models import AdapterResult


def validate_registry(municipalities: list[dict[str, str]]) -> set[str]:
    """Reject incomplete, duplicated or non-Avellino municipal registries."""
    codes = {row['code'] for row in municipalities}
    if len(municipalities) != 118 or len(codes) != 118:
        raise ValueError(f'Expected 118 unique municipalities, got {len(municipalities)} rows / {len(codes)} codes')
    if any(len(code) != 6 or not code.isdigit() or not code.startswith('064') for code in codes):
        raise ValueError('Registry contains invalid ISTAT municipal codes')
    if any(row['province_code'] != '064' or not row['name'].strip() for row in municipalities):
        raise ValueError('Registry province or municipality name is invalid')
    return codes


def assess(result: AdapterResult, known_codes: set[str]) -> dict[str, object]:
    """Reject ambiguous records and calculate coverage for each indicator/period."""
    indicators = {str(row['id']) for row in result.metadata['indicators']}
    if result.metadata['status'] not in ('ready', 'blocked'):
        raise ValueError('Invalid dataset status')
    if result.metadata['status'] == 'blocked' and ((result.observations or result.entities) or not result.metadata.get('blocker')):
        raise ValueError('Blocked datasets require an explicit blocker and no observations')
    if result.metadata['status'] == 'ready' and not (result.observations or result.entities):
        raise ValueError('Ready dataset has no verified observations')
    keys: set[tuple[str, str, str]] = set()
    coverage: dict[tuple[str, str], dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for indicator_id in indicators:
        periods = {item.period for item in result.observations if item.indicator_id == indicator_id}
        for period in periods or {str(result.metadata.get('period', 'unavailable'))}:
            coverage[(indicator_id, period)]
    for observation in result.observations:
        key = (observation.municipality_code, observation.indicator_id, observation.period)
        if key in keys:
            raise ValueError(f'Duplicate observation: {key}')
        keys.add(key)
        if observation.municipality_code not in known_codes:
            raise ValueError(f'Unreconciled municipal code: {observation.municipality_code}')
        if observation.indicator_id not in indicators:
            raise ValueError(f'Unknown indicator: {observation.indicator_id}')
        if not observation.period or observation.status not in ('observed', 'missing', 'suppressed'):
            raise ValueError(f'Invalid period or status: {key}')
        if observation.status == 'observed':
            if observation.value is None or not isfinite(observation.value):
                raise ValueError(f'Observed value must be finite: {key}')
            definition = next(row for row in result.metadata['indicators'] if row['id'] == observation.indicator_id)
            if observation.value < 0 and not definition.get('allow_negative', False):
                raise ValueError(f'Negative value for nonnegative prototype indicator: {key}')
            if str(next(row['unit'] for row in result.metadata['indicators'] if row['id'] == observation.indicator_id)) == '%' and observation.value > 100:
                raise ValueError(f'Percentage exceeds 100: {key}')
        elif observation.value is not None:
            raise ValueError(f'Missing/suppressed values must be null: {key}')
        coverage[(observation.indicator_id, observation.period)][observation.status].add(observation.municipality_code)
    entity_keys: set[tuple[str, str]] = set()
    for entity in result.entities:
        key = (entity.dataset_id, entity.source_id)
        if key in entity_keys or entity.dataset_id != result.metadata['id']:
            raise ValueError(f'Duplicate or foreign entity: {key}')
        if (entity.municipality_code is not None and entity.municipality_code not in known_codes) or not entity.title.strip():
            raise ValueError(f'Unreconciled entity: {key}')
        entity_keys.add(key)
    groups = []
    for (indicator_id, period), states in sorted(coverage.items()):
        present = set().union(*states.values())
        groups.append({'indicator_id': indicator_id, 'period': period, 'expected': len(known_codes),
                       'observed': len(states['observed']), 'suppressed': len(states['suppressed']),
                       'missing': len(states['missing']), 'absent': len(known_codes - present),
                       'missing_codes': sorted(known_codes - states['observed'])})
    return {'dataset_id': result.metadata['id'], 'status': result.metadata['status'],
            'rows': len(result.observations), 'entities': len(result.entities), 'groups': groups,
            'blocker': result.metadata.get('blocker')}
