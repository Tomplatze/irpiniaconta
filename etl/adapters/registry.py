"""Reconcile municipalities against the official ISTAT administrative register."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from zipfile import ZipFile

from etl.acquisition import Context
from etl.models import AdapterResult

LANDING_URL = 'https://www.istat.it/classificazione/codici-dei-comuni-delle-province-e-delle-regioni/'
DOWNLOAD_URL = 'https://www.istat.it/storage/codici-unita-amministrative/Elenco-comuni-italiani.xlsx'
LICENSE_URL = 'https://www.istat.it/note-legali/'
METADATA: dict[str, object] = {
    'id': 'istat_registry', 'name': 'ISTAT official municipality register',
    'publisher': 'ISTAT', 'landing_url': LANDING_URL, 'download_url': DOWNLOAD_URL,
    'license': 'CC-BY-4.0 (ISTAT default unless otherwise indicated)',
    'license_url': LICENSE_URL, 'format': 'XLSX', 'geography': 'Municipality',
    'period': '2026-02-21', 'status': 'ready', 'blocker': None,
    'notes': 'Official register downloaded from the permanent URL; filter historical province code 064 and region 15. Codes remain six-character strings.',
    'indicators': [],
}
_NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def parse_register(path: Path) -> list[dict[str, str]]:
    """Read the official XLSX without dependencies and assert its geographic scope."""
    with ZipFile(path) as archive:
        strings = [''.join(item.itertext()) for item in ET.fromstring(archive.read('xl/sharedStrings.xml'))]
        sheet = ET.fromstring(archive.read('xl/worksheets/sheet1.xml'))
    sheet_data = sheet.find('s:sheetData', _NS)
    if sheet_data is None:
        raise ValueError('ISTAT registry contains no worksheet data')
    records: list[dict[str, str]] = []
    for row in sheet_data:
        cells: dict[str, str] = {}
        for cell in row:
            column = re.sub(r'\d', '', cell.attrib['r'])
            node = cell.find('s:v', _NS)
            value = node.text or '' if node is not None else ''
            cells[column] = strings[int(value)] if cell.attrib.get('t') == 's' else value
        records.append(cells)
    header = records[0]
    expected = {'A': 'Codice Regione', 'E': 'Codice Comune formato alfanumerico', 'G': 'Denominazione in italiano'}
    if any(header.get(column) != label for column, label in expected.items()):
        raise ValueError('ISTAT registry schema changed; inspect the original workbook')
    municipalities = [
        {'code': row['E'], 'name': row['G'], 'province_code': row['C'], 'region_code': row['A']}
        for row in records[1:] if row.get('C') == '064'
    ]
    codes = [item['code'] for item in municipalities]
    if len(municipalities) != 118 or len(set(codes)) != 118:
        raise ValueError(f'Expected 118 distinct Avellino municipalities; received {len(municipalities)}')
    if any(not re.fullmatch(r'064\d{3}', code) for code in codes):
        raise ValueError('Municipality codes are not valid six-character Avellino ISTAT codes')
    if any(item['region_code'] != '15' or not item['name'] for item in municipalities):
        raise ValueError('Invalid Campania municipality in ISTAT register')
    return sorted(municipalities, key=lambda item: item['code'])


def run(context: Context) -> AdapterResult:
    """Download or checksum-replay the register and return the 118 authoritative codes."""
    path = context.fetch(DOWNLOAD_URL, 'istat_registry_2026.xlsx')
    return AdapterResult(dict(METADATA), municipalities=parse_register(path))
