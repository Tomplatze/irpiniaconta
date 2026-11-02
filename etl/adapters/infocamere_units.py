"""Verify the supplied InfoCamere lead and expose its geographic blocker."""
import csv
import io
import re
from copy import deepcopy

from etl.acquisition import Context
from etl.models import AdapterResult, Observation, ValueStatus

LANDING_URL = 'https://www.dati.gov.it/node/view-dataset/dataset?id=d92d4eb9-077e-4c05-a05e-fa833aabd490'
CATALOG_URL = 'https://dati.toscana.it/api/3/action/package_show?id=e3879a61-c73b-4457-a1b7-f2720eb8956a'
DOWNLOAD_URL = 'https://dati.toscana.it/dataset/e3879a61-c73b-4457-a1b7-f2720eb8956a/resource/f5e43d7d-21ed-4d30-aa2d-fce7dd421d0c/download/unitalocali2025.csv'
METADATA: dict[str, object] = {
    'id': 'infocamere_units',
    'name': 'Unità locali InfoCamere',
    'publisher': 'Regione Toscana — Ufficio Regionale di Statistica; source InfoCamere',
    'landing_url': LANDING_URL,
    'download_url': DOWNLOAD_URL,
    'license': 'Conflicting metadata: CC BY 4.0 (dati.gov.it resource), CC BY-SA (Tuscany CKAN package)',
    'license_url': 'https://w3id.org/italia/controlled-vocabulary/licences/A21_CCBY40',
    'format': 'CSV (Windows-1252, comma)',
    'geography': 'Tuscany only; NOT Avellino',
    'period': '2025',
    'status': 'blocked',
    'blocker': 'The verified public CSV covers Tuscany only (0 Avellino codes). No reusable municipal Avellino distribution was verified. Obtain a licensed Stockview export from CCIAA Irpinia Sannio. Source licence metadata also conflicts.',
    'notes': [
        'Supplied catalog lead d92d4eb9-077e-4c05-a05e-fa833aabd490 is not a national municipal dataset.',
        'Downloaded 4,738 sector-level rows, 277 municipal codes including unassigned 000 rows, and 10 Tuscany provinces; zero codes beginning 064.',
        'The municipal schema is verified for the Tuscany example only. Municipal Avellino schema, period and reuse licence remain unverified.',
        'Public Movimprese and national CCIAA Marche data provide province-level statistics. They cannot support municipal comparisons.',
        'CCIAA Irpinia Sannio confirms Stockview municipal statistics exist and says municipal reports can be requested. No request was sent.',
    ],
    'indicators': [
        {'id': 'active_local_units', 'label': 'Unità locali attive', 'unit': 'local units', 'definition': 'Planned municipal total of UL_Attive across disjoint ATECO sections; no values loaded because Avellino coverage is absent.'},
    ],
}


def parse_units(payload: bytes) -> tuple[list[Observation], int, int]:
    """Validate the downloaded example; never invent absent municipal totals."""
    text = payload.decode('cp1252')
    reader = csv.DictReader(io.StringIO(text), delimiter=',')
    required = {'Anno', 'Cod_Istat_Provincia', 'Cod_Istat_Comune', 'Cod_Sezione', 'UL_Attive'}
    if not required.issubset(reader.fieldnames or []):
        raise ValueError('InfoCamere example schema changed')
    totals: dict[tuple[str, str], float | None] = {}
    statuses: dict[tuple[str, str], ValueStatus] = {}
    seen: set[tuple[str, str, str]] = set()
    municipal_codes: set[str] = set()
    count = 0
    for row in reader:
        count += 1
        code = row['Cod_Istat_Comune'].strip()
        if not re.fullmatch(r'\d{6}', code):
            raise ValueError(f'Invalid municipal code in InfoCamere example: {code!r}')
        municipal_codes.add(code)
        if not code.startswith('064'):
            continue
        if row['Cod_Istat_Provincia'].strip() != '064' or code.endswith('000'):
            raise ValueError('Inconsistent or unassigned Avellino InfoCamere municipal row')
        year = row['Anno'].strip()
        if not re.fullmatch(r'\d{4}', year):
            raise ValueError('Invalid InfoCamere reference year')
        section = row['Cod_Sezione'].strip()
        if not re.fullmatch(r'[A-U]|nd', section):
            raise ValueError('Expected disjoint ATECO sections; totals must not be summed twice')
        key = (code, year, section)
        if key in seen:
            raise ValueError(f'Duplicate InfoCamere sector row: {key}')
        seen.add(key)
        raw = row['UL_Attive'].strip()
        group = (code, year)
        if not raw or raw in {'*', '..', '...'}:
            totals[group] = None
            if raw or statuses.get(group) == 'suppressed':
                statuses[group] = 'suppressed'
            else:
                statuses[group] = 'missing'
        elif re.fullmatch(r'\d+', raw):
            if group not in totals:
                totals[group] = 0.0
                statuses[group] = 'observed'
            if totals[group] is not None:
                totals[group] += float(raw)
        else:
            raise ValueError(f'Unexpected InfoCamere count: {raw!r}')
    observations = [Observation(code, 'active_local_units', year, value, statuses[(code, year)])
                    for (code, year), value in sorted(totals.items())]
    return observations, count, len(municipal_codes)


def run(context: Context) -> AdapterResult:
    """Recheck public artifacts and return an explicit empty blocked result."""
    metadata = deepcopy(METADATA)
    context.fetch(CATALOG_URL, 'infocamere-toscana-2025-catalog.json')
    path = context.fetch(DOWNLOAD_URL, 'infocamere-toscana-units-2025.csv')
    observations, rows, codes = parse_units(path.read_bytes())
    if observations:
        raise ValueError('InfoCamere source geography changed; verify new Avellino coverage and licence before import')
    metadata['verification'] = {'source_rows': rows, 'source_municipal_codes': codes, 'target_municipal_codes': 0}
    return AdapterResult(metadata)
