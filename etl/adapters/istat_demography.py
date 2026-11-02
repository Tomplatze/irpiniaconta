"""Import actual ISTAT municipal population estimates, with age-total validation."""
from collections import defaultdict
from pathlib import Path
import csv
import io
import re
from zipfile import ZipFile
from urllib.parse import urljoin
from copy import deepcopy

from etl.acquisition import Context
from etl.models import AdapterResult, Observation, ValueStatus

LANDING_URL = 'https://demo.istat.it/app/?i=POS&l=it'
DOWNLOAD_URL = 'https://demo.istat.it/data/posas/POSAS_2026_it_064_Avellino.zip'
PERIOD = '2026-01-01'
METADATA: dict[str, object] = {
    'id': 'istat_demography', 'name': 'Resident population by age and sex, 1 January 2026 (estimate)',
    'publisher': 'ISTAT', 'landing_url': LANDING_URL, 'download_url': DOWNLOAD_URL,
    'license': 'CC-BY-4.0 (ISTAT default unless otherwise indicated)',
    'license_url': 'https://www.istat.it/note-legali/', 'format': 'ZIP / UTF-8 semicolon CSV',
    'geography': 'Municipality', 'period': PERIOD, 'status': 'ready', 'blocker': None,
    'notes': 'The original CSV explicitly labels 2026 values as estimates, aligned with census results and provisional 2025 demographic balance. Not the final census count. Age 999 is the total; it is never summed as an age. Derived percentages are computed from age rows.',
    'indicators': [
        {'id': 'population', 'label': 'Popolazione residente (stima)', 'unit': 'persons',
         'definition': 'ISTAT resident population estimate on 1 January 2026, both sexes, original age-999 total.'},
        {'id': 'population_65_plus_share', 'label': 'Residenti di almeno 65 anni (stima)', 'unit': '%',
         'definition': '100 × sum of estimated resident population in age rows 65–100 / age-999 population total, both sexes.'},
    ],
}
_COLUMNS = ['Codice comune', 'Comune', 'Età', 'Totale maschi', 'Totale femmine', 'Totale']


def parse_count(raw: str | None) -> tuple[int | None, ValueStatus]:
    """Preserve missing/suppressed source tokens; reject ambiguous numeric formats."""
    if raw is None or raw.strip() in {'', '..', '...'}:
        return None, 'missing'
    if raw.strip() in {'*', '**', 'x', 'X'}:
        return None, 'suppressed'
    if not re.fullmatch(r'\d+', raw.strip()):
        raise ValueError(f'Unexpected ISTAT population value: {raw!r}')
    return int(raw), 'observed'


def parse_population(path: Path, year: int = 2026) -> list[Observation]:
    """Verify the published schema, all ages and sex totals before normalization."""
    with ZipFile(path) as archive:
        members = [name for name in archive.namelist() if name.endswith('.csv')]
        if members != [f'POSAS_{year}_it_064_Avellino.csv']:
            raise ValueError('Unexpected ISTAT population ZIP members')
        content = archive.read(members[0]).decode('utf-8-sig')
    lines = content.splitlines()
    if str(year) not in lines[0]:
        raise ValueError('ISTAT estimate period/title differs from the pinned source')
    reader = csv.DictReader(io.StringIO('\n'.join(lines[1:])), delimiter=';')
    if reader.fieldnames != _COLUMNS:
        raise ValueError('ISTAT population CSV schema changed')
    by_code: dict[str, dict[int, tuple[int | None, ValueStatus]]] = defaultdict(dict)
    for row in reader:
        code = row['Codice comune']
        if row['Età'] is None and code == 'Nota: lo stato civile è in corso di validazione.':
            continue
        if not re.fullmatch(r'064\d{3}', code):
            raise ValueError(f'Unexpected population geography or footer: {code}')
        age_text = row['Età']
        if age_text is None or not age_text.isdigit():
            raise ValueError('Invalid population age')
        age = int(age_text)
        if age in by_code[code] or age not in {*range(101), 999}:
            raise ValueError(f'Duplicate/unexpected age {age} for {code}')
        male, male_status = parse_count(row['Totale maschi'])
        female, female_status = parse_count(row['Totale femmine'])
        total, total_status = parse_count(row['Totale'])
        if male_status == female_status == total_status == 'observed' and total != (male or 0) + (female or 0):
            raise ValueError(f'Sex totals do not reconcile for {code}, age {age}')
        by_code[code][age] = (total, total_status)
    if len(by_code) != 118:
        raise ValueError(f'Expected 118 population municipalities; received {len(by_code)}')
    period = f'{year}-01-01'
    observations: list[Observation] = []
    for code, ages in sorted(by_code.items()):
        if set(ages) != {*range(101), 999}:
            raise ValueError(f'Incomplete age coverage for {code}')
        population, status = ages[999]
        age_values = [ages[age][0] for age in range(101)]
        if population is not None and all(value is not None for value in age_values):
            if sum(value for value in age_values if value is not None) != population:
                raise ValueError(f'Age population sum does not match published total for {code}')
        observations.append(Observation(code, 'population', period, float(population) if population is not None else None, status))
        selected = [ages[age] for age in range(65, 101)]
        derived_status: ValueStatus = 'suppressed' if any(item[1] == 'suppressed' for item in selected) or status == 'suppressed' else 'missing'
        share: float | None = None
        if population is not None and population > 0 and all(item[0] is not None for item in selected):
            share = 100 * sum(item[0] for item in selected if item[0] is not None) / population
            derived_status = 'observed'
        observations.append(Observation(code, 'population_65_plus_share', period, share, derived_status))
    return observations


def run(context: Context) -> AdapterResult:
    """Discover the current province archive and validate the actual source period/schema."""
    landing = context.fetch(LANDING_URL, 'istat_demo_landing.html').read_text()
    links = re.findall(r'href="([^\"]*POSAS_(\d{4})_it_064_Avellino\.zip)"', landing)
    if not links: raise ValueError('ISTAT current population archive discovery failed')
    link, year = max(links, key=lambda item: int(item[1]))
    url = urljoin(LANDING_URL, link)
    filename = f'istat_demography_{year}_avellino.zip'
    path = context.fetch(url, filename)
    metadata = deepcopy(METADATA)
    metadata['period'] = f'{year}-01-01'
    metadata['download_url'] = url
    metadata['name'] = f'Resident population by age and sex, 1 January {year}'
    with ZipFile(path) as archive:
        title = archive.read(archive.namelist()[0]).decode('utf-8-sig').splitlines()[0]
    metadata['source_title'] = title
    metadata['notes'] = 'Source title: ' + title + '. Age 999 is the original total. Age-derived shares are deterministic. Historical demographic balances are stored separately; missing values are not reconstructed.'
    return AdapterResult(metadata, observations=parse_population(path, int(year)))
