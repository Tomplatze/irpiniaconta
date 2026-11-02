"""Normalize the verified MEF municipal IRPEF archive, without imputing blanks."""
import csv
import io
import math
import re
import zipfile
from copy import deepcopy
from urllib.parse import urljoin

from etl.acquisition import Context
from etl.models import AdapterResult, Observation, ValueStatus

LANDING_URL = 'https://www1.finanze.gov.it/finanze/analisi_stat/public/index.php?opendata=yes&search_class%5B0%5D=cCOMUNE'
DOWNLOAD_URL = 'https://www1.finanze.gov.it/finanze/analisi_stat/public/v_4_0_0/contenuti/Redditi_e_principali_variabili_IRPEF_su_base_comunale_CSV_2024.zip?d=1615465800'
PERIOD = '2024'
FIELDS = {
    'irpef_taxpayers': 'Numero contribuenti',
    'irpef_income_declarants': 'Reddito complessivo - Frequenza',
    'irpef_income_total': 'Reddito complessivo - Ammontare in euro',
}
METADATA: dict[str, object] = {
    'id': 'mef_irpef',
    'name': 'Redditi IRPEF comunali',
    'publisher': 'MEF — Dipartimento delle Finanze',
    'landing_url': LANDING_URL,
    'download_url': DOWNLOAD_URL,
    'license': 'CC BY 3.0 IT (official landing page)',
    'license_url': 'https://creativecommons.org/licenses/by/3.0/it/',
    'format': 'ZIP / CSV (UTF-8, semicolon)',
    'geography': 'Italy; municipality ISTAT code; prototype filters province 064',
    'period': PERIOD,
    'status': 'ready',
    'blocker': None,
    'notes': [
        'Tax year 2024; declaration year 2025; published 23 April 2026. Latest downloadable municipal archive verified on 12 October 2026.',
        'MEF landing HTML links CC BY 3.0 IT; its RDF archive links generic CC BY 3.0. Attribution: MEF — Dipartimento delle Finanze. See docs/evidence/mef-income.md.',
        'The derived mean divides total overall declared income by its own frequency, not by residents or all taxpayers. It is not disposable household income.',
        'Blank fields remain null; no reconstruction of suppressed income brackets.',
    ],
    'indicators': [
        {'id': 'irpef_taxpayers', 'label': 'Contribuenti IRPEF', 'unit': 'persons', 'definition': 'MEF Numero contribuenti, tax year 2024.'},
        {'id': 'irpef_income_declarants', 'label': 'Dichiaranti reddito complessivo', 'unit': 'persons', 'definition': 'MEF Reddito complessivo - Frequenza; denominator for the mean.'},
        {'id': 'irpef_income_total', 'label': 'Reddito complessivo dichiarato', 'unit': 'EUR', 'definition': 'MEF Reddito complessivo - Ammontare in euro; nominal annual total.'},
        {'id': 'irpef_income_mean', 'label': 'Reddito medio per dichiarante', 'unit': 'EUR/person', 'definition': 'Derived: Reddito complessivo - Ammontare in euro / Reddito complessivo - Frequenza; not per resident.'},
    ],
}


def parse_number(raw: str) -> tuple[float | None, ValueStatus]:
    """Keep an explicit zero distinct from a missing or suppressed measurement."""
    token = raw.strip()
    if not token:
        return None, 'missing'
    if token in {'*', '**', '***', '..', '...'}:
        return None, 'suppressed'
    if not re.fullmatch(r'-?\d+', token):
        raise ValueError(f'Unexpected MEF integer token: {token!r}')
    value = float(token)
    if not math.isfinite(value):
        raise ValueError('Non-finite MEF measurement')
    return value, 'observed'


def parse_archive(payload: bytes, period: str = PERIOD) -> list[Observation]:
    """Require the observed schema and select exact six-digit Avellino codes."""
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        filenames = [name for name in archive.namelist() if name.lower().endswith('.csv')]
        if len(filenames) != 1:
            raise ValueError('Expected exactly one MEF CSV archive member')
        text = archive.read(filenames[0]).decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(text), delimiter=';')
    required = {'Anno di imposta', 'Codice Istat Comune', 'Sigla Provincia', *FIELDS.values()}
    if not required.issubset(reader.fieldnames or []):
        raise ValueError('MEF schema changed: expected municipal identifiers and income fields')
    observations: list[Observation] = []
    seen: set[str] = set()
    for row in reader:
        code = row['Codice Istat Comune'].strip()
        if not code.startswith('064'):
            continue
        if not re.fullmatch(r'064\d{3}', code) or row['Sigla Provincia'] != 'AV':
            raise ValueError(f'Invalid Avellino MEF municipality: {code!r}')
        if row['Anno di imposta'] != period:
            raise ValueError('MEF period differs from the verified archive year')
        if code in seen:
            raise ValueError(f'Duplicate MEF municipal row: {code}')
        seen.add(code)
        parsed = {indicator: parse_number(row[field]) for indicator, field in FIELDS.items()}
        for indicator, (value, status) in parsed.items():
            if value is not None and value < 0:
                raise ValueError(f'Negative selected MEF measurement: {code}/{indicator}')
            observations.append(Observation(code, indicator, period, value, status))
        total, total_status = parsed['irpef_income_total']
        frequency, frequency_status = parsed['irpef_income_declarants']
        if total is not None and frequency is not None and frequency > 0:
            observations.append(Observation(code, 'irpef_income_mean', period, total / frequency))
        else:
            status: ValueStatus = 'suppressed' if 'suppressed' in {total_status, frequency_status} else 'missing'
            observations.append(Observation(code, 'irpef_income_mean', period, None, status))
    if not seen:
        raise ValueError('MEF archive contains no Avellino municipal rows')
    return observations


def run(context: Context, options: dict[str, object] | None = None) -> AdapterResult:
    """Discover municipal archives in the official catalogue and import every configured tax year."""
    metadata = deepcopy(METADATA)
    landing = context.fetch(LANDING_URL, 'mef-catalog.html').read_text(encoding='utf-8')
    if 'creativecommons.org/licenses/by/3.0/it/' not in landing:
        raise ValueError('MEF landing licence changed; manual verification required')
    links = dict((year, urljoin(LANDING_URL, url)) for url, year in re.findall(
        r'href="([^\"]*Redditi_e_principali_variabili_IRPEF_su_base_comunale_CSV_(\d{4})[^\"]*)"', landing))
    start_year = int((options or {}).get('start_year', 2020))
    years = sorted(year for year in links if int(year) >= start_year)
    if not years: raise ValueError('No configured MEF archive years discovered')
    observations = []
    for year in years:
        observations.extend(parse_archive(context.fetch(links[year], f'mef-income-{year}.zip').read_bytes(), year))
    metadata['period'] = f'{years[0]}–{years[-1]}'
    metadata['download_url'] = links[years[-1]]
    metadata['notes'] = [
        'Tax year is the observation period; declaration/release year is different. Nominal annual amounts, not inflation-adjusted.',
        'MEF municipal CSV archives discovered from the official current catalogue; original observations retained by period.',
        'The derived mean divides overall declared income by its own declaration frequency, not residents or all taxpayers.',
        'Missing and suppressed values remain distinct. Licence: official landing CC BY 3.0 IT.'
    ]
    for item in metadata['indicators']:
        item['definition'] = str(item['definition']).replace('tax year 2024', 'explicit tax year')
    return AdapterResult(metadata, observations)
