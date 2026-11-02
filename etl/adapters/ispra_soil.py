"""Ingest the official ISPRA municipal soil-consumption workbook, edition 2025."""
from copy import deepcopy
import math
from pathlib import Path

from openpyxl import load_workbook

from etl.acquisition import Context
from etl.models import AdapterResult, Observation, ValueStatus

LANDING_URL = (
    'https://www.isprambiente.gov.it/it/attivita/suolo-e-territorio/suolo/'
    'il-consumo-di-suolo/i-dati-sul-consumo-di-suolo'
)
DOWNLOAD_URL = (
    'https://www.isprambiente.gov.it/it/attivita/suolo-e-territorio/suolo/'
    'il-consumo-di-suolo/consumo_di_suolo_estratto_dati_2025_anni_2006_2024.xlsx'
)
LICENSE_EVIDENCE_URL = (
    'https://www.isprambiente.gov.it/it/attivita/suolo-e-territorio/suolo/'
    'il-consumo-di-suolo/la-misura-del-consumo-di-suolo'
)
PERIOD = '2024'
FIELDS = {
    'Suolo consumato 2024 [ettari]': 'soil_consumed_ha',
    'Suolo consumato 2024 [%]': 'soil_consumed_pct',
    'Incremento netto 2023-2024 [ettari]': 'soil_net_change_ha',
}

METADATA: dict[str, object] = {
    'id': 'ispra_soil',
    'name': 'ISPRA — Consumo di suolo comunale',
    'publisher': 'ISPRA / Sistema Nazionale per la Protezione dell’Ambiente',
    'landing_url': LANDING_URL,
    'download_url': DOWNLOAD_URL,
    'license': 'CC BY 3.0 IT',
    'license_url': 'https://creativecommons.org/licenses/by/3.0/it/',
    'format': 'XLSX',
    'geography': 'Comune; Italian national workbook filtered by ISTAT prefix 064',
    'period': PERIOD,
    'status': 'ready',
    'blocker': None,
    'notes': (
        'Report edition 2025 contains observations for 2024, not 2025. '
        'The official 2025 preliminary-data notice states that definitive 2025 '
        'data are expected at the end of October 2026. Verified on 2026-10-12. '
        'PRO_COM is padded to six digits; missing cells remain null. '
        'Workbook percentages retain more precision than the public map API. '
        f'Licence declaration: {LICENSE_EVIDENCE_URL}. '
        'Net change may be negative because restored land is deducted.'
    ),
    'indicators': [
        {
            'id': 'soil_consumed_ha',
            'label': 'Suolo consumato',
            'unit': 'ha',
            'definition': 'Total artificial land surface observed in 2024, in hectares.',
        },
        {
            'id': 'soil_consumed_pct',
            'label': 'Quota di suolo consumato',
            'unit': '%',
            'definition': 'Artificial surface as a percentage of municipal territorial surface in 2024.',
        },
        {
            'id': 'soil_net_change_ha',
            'label': 'Consumo netto di suolo',
            'unit': 'ha',
            'allow_negative': True,
            'definition': 'Increase in consumed land minus restored land between 2023 and 2024.',
        },
    ],
}


def measurement(value: object) -> tuple[float | None, ValueStatus]:
    """Preserve published zero, missingness and suppression as separate states."""
    if value is None or value == '':
        return None, 'missing'
    if isinstance(value, str) and value.strip() in {'..', '...', '*', 's', 'S'}:
        return None, 'suppressed'
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f'Unexpected ISPRA measurement: {value!r}')
    number = float(value)
    if not math.isfinite(number):
        raise ValueError('Non-finite ISPRA measurement')
    return number, 'observed'


def parse_workbook(path: Path) -> list[Observation]:
    """Normalize only municipality-coded Avellino rows with verified headers."""
    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        sheet = workbook['Comuni_2006_2024']
        rows = sheet.iter_rows(values_only=True)
        headers = next(rows)
        required = {'PRO_COM', 'Nome_Provincia', *FIELDS}
        missing = required.difference(headers)
        if missing:
            raise ValueError(f'ISPRA workbook schema changed; missing columns: {sorted(missing)}')
        columns = {str(name): index for index, name in enumerate(headers)}
        observations: list[Observation] = []
        seen: set[str] = set()
        for row in rows:
            raw_code = row[columns['PRO_COM']]
            if raw_code is None:
                continue
            if isinstance(raw_code, bool):
                raise ValueError('Invalid ISPRA municipality code')
            code = str(raw_code).removesuffix('.0').zfill(6)
            if not code.startswith('064'):
                continue
            if not code.isdigit() or len(code) != 6:
                raise ValueError(f'Invalid ISPRA municipality code: {raw_code!r}')
            if row[columns['Nome_Provincia']] != 'Avellino':
                raise ValueError(f'ISPRA province mismatch for {code}')
            if code in seen:
                raise ValueError(f'Duplicate ISPRA municipality code: {code}')
            seen.add(code)
            for field, indicator_id in FIELDS.items():
                value, status = measurement(row[columns[field]])
                observations.append(Observation(code, indicator_id, PERIOD, value, status))
        if len(seen) != 118:
            raise ValueError(f'ISPRA municipal coverage changed: expected 118, found {len(seen)}')
        return observations
    finally:
        workbook.close()


def run(context: Context) -> AdapterResult:
    """Acquire the official workbook and licence declaration with hash evidence."""
    path = context.fetch(DOWNLOAD_URL, 'ispra_indicator_definitions_2025.xlsx')
    license_path = context.fetch(LICENSE_EVIDENCE_URL, 'ispra_license.html')
    if 'CC BY 3.0 IT' not in license_path.read_text(encoding='utf-8'):
        raise ValueError('ISPRA licence declaration changed; review reuse terms')
    return AdapterResult(deepcopy(METADATA), parse_workbook(path))
