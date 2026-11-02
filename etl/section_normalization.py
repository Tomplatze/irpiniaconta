"""Deterministic, reviewed transformations from source-field staging to public metrics."""
from __future__ import annotations
from collections import defaultdict
from datetime import date
from pathlib import Path
import calendar
import gzip
import hashlib
import json
import math
import re


def source_rows(root: Path, dataset: dict):
    """Verify each declared staged artifact before streaming its original-field rows."""
    path = root / dataset['staging_file']
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != dataset['staging_sha256']:
        raise ValueError(f"Staging checksum mismatch: {dataset['id']}")
    with gzip.open(path, 'rt', encoding='utf-8') as handle:
        for line in handle:
            yield json.loads(line)


def number(value: object, mode: str = 'native') -> tuple[float | None, str]:
    """Parse only the declared source numeric convention; no missing token becomes zero."""
    if value is None or isinstance(value, str) and value.strip() in {'', '-', '..', '...', 'n.d.', '#VALUE!', '#REF!', '#N/A', '#DIV/0!'}:
        return None, 'missing'
    if isinstance(value, bool):
        raise ValueError('Boolean is not a measurement')
    if isinstance(value, str):
        raw = value.strip().removesuffix('%').strip()
        if mode == 'italian':
            if not re.fullmatch(r'-?(?:\d+|\d{1,3}(?:\.\d{3})+)(?:,\d+)?', raw):
                raise ValueError(f'Invalid Italian numeric token: {value!r}')
            raw = raw.replace('.', '').replace(',', '.')
        elif not re.fullmatch(r'-?\d+(?:\.\d+)?', raw):
            raise ValueError(f'Invalid source numeric token: {value!r}')
        result = float(raw)
    elif isinstance(value, (int, float)):
        result = float(value)
    else:
        raise ValueError(f'Unsupported numeric value: {value!r}')
    if not math.isfinite(result):
        raise ValueError('Non-finite source measurement')
    return result, 'observed'


def observed_value(source: dict, recipe: dict) -> tuple[float | None, str]:
    """Honor both disclosure and source anomaly flags before publishing a value."""
    if recipe.get('flags'):
        if str(source.get('Privacy', '')).strip():
            return None, 'suppressed'
        if str(source.get('Anomalia', '')).strip():
            return None, 'missing'
    flag = str(source.get('source_status') or source.get('Flags') or '').strip()
    if flag == 'c':
        return None, 'suppressed'
    if flag in {'g', 'GI', 'Z', '-'}:
        return None, 'missing'
    if flag not in {'', 'e', 'p', 'r'}:
        raise ValueError(f'Unreviewed source status: {flag}')
    return number(source.get(recipe['value']), recipe.get('number_format', 'native'))


def cell(code: str, period: str, value: float | None, status: str, weight: float | None = None) -> dict:
    """Build a normalized cell retaining an optional same-source denominator."""
    return {'code': code, 'period': period, 'value': value, 'status': status, 'weight': weight}


def matches(source: dict, filters: dict) -> bool:
    """Match declared source codes exactly, including explicit disjoint category sets."""
    return all(source.get(key) in value if isinstance(value, list) else source.get(key) == value for key, value in filters.items())


def filtered(root: Path, datasets: list[dict], recipe: dict) -> tuple[list[dict], dict]:
    """Select one reviewed measure and reject duplicate cells or incomplete combinations."""
    grouped: dict[tuple[str, str], list[tuple[float | None, str]]] = defaultdict(list)
    list_filters = [value for value in recipe['filters'].values() if isinstance(value, list)]
    expected = math.prod(len(values) for values in list_filters) if recipe.get('combine') else 1
    for dataset in datasets:
        for row in source_rows(root, dataset):
            if not matches(row['source'], recipe['filters']):
                continue
            if len(row['municipality_codes']) != 1:
                raise ValueError('A scalar source cell must have exactly one municipal association')
            grouped[row['municipality_codes'][0], row['period']].append(observed_value(row['source'], recipe))
    cells = []
    for (code, period), values in grouped.items():
        if len(values) > expected:
            raise ValueError(f'Duplicate selected source cells: {code}/{period}')
        status = 'suppressed' if any(status == 'suppressed' for _, status in values) else 'missing'
        valid = len(values) == expected and all(status == 'observed' for _, status in values)
        cells.append(cell(code, period, sum(value for value, _ in values if value is not None) if valid else None, 'observed' if valid else status))
    return cells, {}


def foreign_residents(root: Path, datasets: list[dict], recipe: dict) -> tuple[list[dict], dict]:
    """Use ISTAT's age-999 totals after reconciling both sexes against ages 0–100."""
    groups: dict[tuple[str, str], dict[str, dict]] = defaultdict(dict)
    expected_ages = {str(value) for value in range(101)} | {'999'}
    for dataset in datasets:
        for row in source_rows(root, dataset):
            source = row['source']
            codes = row['municipality_codes']
            period = row['period']
            age = str(source.get('Età', '')).strip()
            if len(codes) != 1 or source.get('Codice comune') != codes[0] or not re.fullmatch(r'\d{4}', period):
                raise ValueError('Invalid foreign-resident municipality or period')
            if age not in expected_ages:
                raise ValueError(f'Unexpected foreign-resident age: {age}')
            key = codes[0], f'{period}-01-01'
            if age in groups[key]:
                raise ValueError(f'Duplicate foreign-resident age: {key}/{age}')
            groups[key][age] = source
    cells = []
    for (code, period), ages in groups.items():
        if set(ages) != expected_ages:
            raise ValueError(f'Incomplete foreign-resident ages: {code}/{period}')
        totals = []
        for field in ('Maschi', 'Femmine'):
            values = [number(ages[str(age)].get(field)) for age in range(101)]
            total, status = number(ages['999'].get(field))
            all_values = values + [(total, status)]
            if any(state != 'observed' for _, state in all_values):
                totals = []
                break
            if any(value is None or value < 0 or not value.is_integer() for value, _ in all_values):
                raise ValueError(f'Invalid foreign-resident count: {code}/{period}')
            if sum(value for value, _ in values if value is not None) != total:
                raise ValueError(f'Foreign-resident totals do not match ages: {code}/{period}')
            totals.append(total)
        valid = len(totals) == 2
        cells.append(cell(code, period, sum(totals) if valid else None, 'observed' if valid else 'missing'))
    return cells, {}


def nested(source: dict, key: str) -> object:
    """Resolve only authored dotted field paths, never caller-supplied expressions."""
    result: object = source
    for component in key.split('.'):
        result = result.get(component) if isinstance(result, dict) else None
    return result


def distinct(root: Path, datasets: list[dict], recipe: dict) -> tuple[list[dict], dict]:
    """Count source identities once per municipality and once across the province."""
    towns: dict[str, set[tuple]] = defaultdict(set)
    regional: set[tuple] = set()
    for dataset in datasets:
        for row in source_rows(root, dataset):
            key = tuple(nested(row['source'], key) for key in recipe['keys'])
            if any(item is None or str(item).strip() == '' for item in key):
                raise ValueError('A source record lacks its declared identity')
            regional.add(key)
            for code in row['municipality_codes']:
                towns[code].add(key)
    period = recipe['period']
    return [cell(code, period, float(len(keys)), 'observed') for code, keys in towns.items()], {'regional_distinct': {period: len(regional)}}


def tourism(root: Path, datasets: list[dict], recipe: dict) -> tuple[list[dict], dict]:
    """Use the two disjoint hotel/other totals, checking the original grand-total column."""
    measure = 'Letti / Beds' if recipe['measure'] == 'beds' else 'Numero / Number'
    hotel = f'totale alberghi / hotels total: {measure}'
    other = f'totale extra-alberghieri / total other accommodations: {measure}'
    cells = []
    for dataset in datasets:
        for row in source_rows(root, dataset):
            source = row['source']
            left, ls = number(source.get(hotel))
            right, rs = number(source.get(other))
            total, ts = number(source.get(other + '__2'))
            valid = ls == rs == 'observed'
            result = left + right if valid else None
            if valid and ts == 'observed' and not math.isclose(result, total):
                raise ValueError('Tourism hotel/other totals do not reconcile with the source grand total')
            cells.append(cell(row['municipality_codes'][0], row['period'], result, 'observed' if valid else 'missing'))
    return cells, {}


def waste(root: Path, datasets: list[dict], recipe: dict) -> tuple[list[dict], dict]:
    """Use same-row quantities and denominators; grouped municipal exports are unavailable."""
    cells = []
    for dataset in datasets:
        for row in source_rows(root, dataset):
            source = row['source']
            valid_row = source.get('Dato riferito a', '').strip() == 'Comune'
            total, ts = number(source.get('Totale RU (t)'), 'italian')
            if recipe['measure'] == 'share':
                part, ps = number(source.get('Totale RD (t)'), 'italian')
                denominator, numerator, factor = total, part, 100
                statuses = (ts, ps)
            else:
                population, ps = number(source.get('Popolazione'), 'native')
                denominator, numerator, factor = population, total, 1000
                statuses = (ts, ps)
            valid = valid_row and all(status == 'observed' for status in statuses) and denominator is not None and denominator > 0
            value = factor * numerator / denominator if valid else None
            cells.append(cell(row['municipality_codes'][0], row['period'], value, 'observed' if valid else 'missing', denominator if valid else None))
    return cells, {}


def weather(root: Path, datasets: list[dict], recipe: dict) -> tuple[list[dict], dict]:
    """Publish complete calendar summaries only; one missing day invalidates that summary."""
    days: dict[tuple[str, str], dict[str, float | None]] = defaultdict(dict)
    field = {'temperature': 'temperature_2m_mean', 'hot_days': 'temperature_2m_max', 'frost_days': 'temperature_2m_min'}[recipe['measure']]
    for dataset in datasets:
        for row in source_rows(root, dataset):
            source = row['source']; code = row['municipality_codes'][0]
            if source['grid']['daily_units'].get(field) != '°C' or source['model'] != 'era5_land':
                raise ValueError('Weather model or units changed')
            day = source['date']; parsed = date.fromisoformat(day)
            if day in days[code, str(parsed.year)]:
                raise ValueError('Duplicate weather date')
            value, _ = number(source.get(field))
            days[code, str(parsed.year)][day] = value
    cells, monthly = [], []
    for (code, year), values in days.items():
        expected = 366 if calendar.isleap(int(year)) else 365
        valid = len(values) == expected and all(value is not None for value in values.values())
        actual = [value for value in values.values() if value is not None]
        result = summarize_weather(actual, recipe['measure']) if valid else None
        cells.append(cell(code, year, result, 'observed' if valid else 'missing'))
        if recipe['measure'] == 'temperature':
            for month in range(1, 13):
                period = f'{year}-{month:02d}'
                sample = [value for day, value in values.items() if day.startswith(period)]
                complete = len(sample) == calendar.monthrange(int(year), month)[1] and all(value is not None for value in sample)
                monthly.append(cell(code, period, sum(sample)/len(sample) if complete else None, 'observed' if complete else 'missing'))
    return cells, {'monthly': monthly}


def summarize_weather(values: list[float], measure: str) -> float:
    """Return a mean or threshold-day count, never a synthetic precipitation estimate."""
    if measure == 'temperature':
        return sum(values) / len(values)
    return float(sum(value >= 30 if measure == 'hot_days' else value < 0 for value in values))
