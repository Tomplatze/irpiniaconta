"""Import verified municipal holdings and area from ISTAT's 2020 agriculture census."""
import json
import math
from pathlib import Path

from etl.acquisition import Context
from etl.models import AdapterResult, Observation, ValueStatus
from etl.adapters.registry import DOWNLOAD_URL as REGISTRY_URL, parse_register

LANDING_URL = 'https://www.istat.it/notizia/censimento-agricoltura-2020-online-i-principali-dati/'
FLOW_ID = 'IT1,DF_DCAT_CENSAGRIC2020_SURF_ALL,1.0'
BASE_URL = 'https://esploradati.istat.it/databrowserhub/api/core/'
CATALOG_URL = BASE_URL + 'nodes/2/catalog'
STRUCTURE_URL = BASE_URL + f'nodes/2/datasets/{FLOW_ID}/structure'
EXPORT_URL = BASE_URL + f'nodes/2/datasets/{FLOW_ID}/data'
METADATA: dict[str, object] = {
    'id': 'istat_agriculture', 'name': 'Agriculture census 2020 — holdings and agricultural area',
    'publisher': 'ISTAT', 'landing_url': LANDING_URL, 'download_url': EXPORT_URL,
    'license': 'CC-BY-4.0 (ISTAT default unless otherwise indicated)',
    'license_url': 'https://www.istat.it/note-legali/',
    'format': 'JSON-stat public export API; SDMX-CSV advertised by the official browser',
    'geography': 'Municipality of the holding headquarters, not location of all its land',
    'period': '2020', 'status': 'ready', 'blocker': None,
    'notes': 'Actual read-only POST export verified for all 118 municipalities. TIME_PERIOD must use TimeRange, not CodeValues: an incorrect time filter can return HTTP 200 with no data. Crop reference: agricultural year 2019/2020; holdings assigned to their headquarters. Catalog node 2, flow IT1,DF_DCAT_CENSAGRIC2020_SURF_ALL,1.0. Measures HO (number of farms) and ARU (utilised agricultural area, hectares). Separate land/livestock-location flows exist and must not be mixed with headquarters measures. See docs/evidence/istat_agriculture.md.',
    'indicators': [
        {'id': 'agricultural_holdings', 'label': 'Aziende agricole', 'unit': 'holdings',
         'definition': 'Original HO measure from the 2020 agriculture census, by municipality of holding headquarters; number of farms.'},
        {'id': 'utilised_agricultural_area', 'label': 'Superficie agricola utilizzata', 'unit': 'ha',
         'definition': 'Original ARU measure, hectares, agricultural year 2019/2020, assigned to holding headquarters; not municipal land-cover area.'},
    ],
}


def probe_export(context: Context, codes: list[str]) -> Path:
    """Fetch a read-only POST export, recording the method, complete body and hashes."""
    filename = 'istat_agriculture_2020_avellino.json'
    body: list[dict[str, object]] = [
        {'id': 'FREQ', 'filterValues': ['A'], 'type': 'CodeValues'},
        {'id': 'REF_AREA', 'filterValues': sorted(codes), 'type': 'CodeValues'},
        {'id': 'DATA_TYPE', 'filterValues': ['HO', 'ARU'], 'type': 'CodeValues'},
        {'id': 'TIME_PERIOD', 'type': 'TimeRange', 'from': '2020-01-01', 'to': '2020-12-31'},
    ]
    path = context.fetch(EXPORT_URL, filename, method='POST', body=body)
    document = json.loads(path.read_text())
    if not isinstance(document, dict) or document.get('class') != 'dataset':
        raise ValueError('Agriculture probe response is not a JSON-stat dataset')
    return path


def parse_export(path: Path, expected_codes: set[str]) -> list[Observation]:
    """Decode JSON-stat linear cells using source category order, never sorted names."""
    document = json.loads(path.read_text())
    if document.get('class') != 'dataset' or document.get('version') != '2.0':
        raise ValueError('Agriculture export is not a JSON-stat 2.0 dataset')
    if document.get('id') != ['FREQ', 'REF_AREA', 'DATA_TYPE', 'TIME_PERIOD']:
        raise ValueError('Agriculture dimension order changed or the response is empty')
    if document.get('size') != [1, 118, 2, 1]:
        raise ValueError('Agriculture export does not have 118 municipalities and two measures')
    dimensions = document['dimension']
    categories: dict[str, list[str]] = {}
    for name in document['id']:
        index = dimensions[name]['category']['index']
        if not isinstance(index, list) or len(set(index)) != len(index):
            raise ValueError(f'Unsupported or duplicate JSON-stat category index for {name}')
        categories[name] = index
    if categories['FREQ'] != ['A'] or categories['TIME_PERIOD'] != ['2020']:
        raise ValueError('Agriculture export frequency or period differs from the request')
    codes = categories['REF_AREA']
    if set(codes) != expected_codes or len(codes) != 118:
        raise ValueError('Agriculture geography does not reconcile with all 118 ISTAT codes')
    types = categories['DATA_TYPE']
    labels = dimensions['DATA_TYPE']['category']['label']
    if set(types) != {'HO', 'ARU'} or labels.get('HO') != 'number of farms' or labels.get('ARU') != 'utilised agricultural area - hectares':
        raise ValueError('Agriculture measures or documented units changed')
    attributes = document.get('extension', {}).get('attributes', {})
    for group in attributes.values():
        if group.get('index', {}).get('observation'):
            raise ValueError('Source observation attribute indexes now exist; validate confidentiality flags before ingestion')
        definitions = group.get('series', [])
        for indexed in group.get('index', {}).get('series', []):
            coordinates = indexed['coordinates']
            for definition, value_index in zip(definitions, indexed['attributes'], strict=True):
                if value_index is None:
                    continue
                attribute_id = definition['id']
                attribute_value = definition['values'][value_index]['id']
                if attribute_id == 'UNIT_MULT' and attribute_value != '0':
                    raise ValueError('Agriculture unit multiplier changed; review scaling')
                if attribute_id == 'NOTE_ISTAT_TERR_OFFICIAL_CODE':
                    area_index = coordinates[1]
                    if area_index is not None and attribute_value != codes[area_index]:
                        raise ValueError('Agriculture official territorial attribute does not match its category code')
    values = document['value']
    if not isinstance(values, dict) or any(not key.isdigit() or int(key) >= 236 for key in values):
        raise ValueError('Unsupported or invalid JSON-stat value indexes')
    statuses = document.get('status', {})
    if not isinstance(statuses, dict):
        raise ValueError('Unsupported JSON-stat observation status encoding')
    observations: list[Observation] = []
    for area_index, code in enumerate(codes):
        for type_index, source_type in enumerate(types):
            cell_index = str(area_index * len(types) + type_index)
            raw_value = values.get(cell_index)
            flag = statuses.get(cell_index)
            if flag not in {None, '', 'c', 'e', 'p', 'r', '-', 'g', 'GI', 'Z'}:
                raise ValueError(f'Unreviewed agriculture observation flag: {flag}')
            status: ValueStatus = 'suppressed' if flag == 'c' else 'missing'
            value: float | None = None
            if flag not in {'c', 'g', 'GI', 'Z'} and raw_value is not None:
                if isinstance(raw_value, bool) or not isinstance(raw_value, (int, float)) or not math.isfinite(raw_value) or raw_value < 0:
                    raise ValueError(f'Invalid agriculture value for {code}/{source_type}')
                if source_type == 'HO' and float(raw_value) != int(raw_value):
                    raise ValueError('Agricultural holding counts must be integers')
                value = float(raw_value)
                status = 'observed'
            indicator_id = 'agricultural_holdings' if source_type == 'HO' else 'utilised_agricultural_area'
            observations.append(Observation(code, indicator_id, '2020', value, status))
    return observations


def run(context: Context) -> AdapterResult:
    """Recheck metadata, obtain the municipal export and normalize verified cells."""
    context.fetch(LANDING_URL, 'istat_agriculture_landing.html')
    catalog_path = context.fetch(CATALOG_URL, 'istat_agriculture_catalog_2.json')
    structure_path = context.fetch(STRUCTURE_URL, 'istat_agriculture_structure.json')
    catalog = json.loads(catalog_path.read_text())
    structure = json.loads(structure_path.read_text())
    if FLOW_ID not in catalog.get('datasetMap', {}):
        raise ValueError('Verified agriculture flow is no longer in the official catalog')
    dimensions = [item['id'] for item in structure.get('criteria', [])]
    if dimensions != ['FREQ', 'REF_AREA', 'DATA_TYPE', 'TIME_PERIOD']:
        raise ValueError('Agriculture dimensions changed; inspect the official structure')
    registry_path = context.fetch(REGISTRY_URL, 'istat_registry_2026.xlsx')
    codes = [item['code'] for item in parse_register(registry_path)]
    export_path = probe_export(context, codes)
    return AdapterResult(dict(METADATA), observations=parse_export(export_path, set(codes)))
