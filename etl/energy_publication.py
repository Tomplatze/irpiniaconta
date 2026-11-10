"""Import verified provincial Terna tables and stage a local snapshot object."""
from __future__ import annotations

import argparse
from decimal import Decimal
import gzip
from hashlib import file_digest, sha256
import json
import os
from pathlib import Path
import re
from tempfile import NamedTemporaryFile
from urllib.parse import urlsplit

from psycopg.types.json import Jsonb

from etl.database import PUBLICATION_LOCK, record_import, require_current_schema, semantic_checksum, transaction
from etl.registry import load_scope
from etl.settings import environment_value

ROOT = Path(__file__).resolve().parents[1]
OBJECT_NAME = 'energy.gz'
NUMBER = r'(?:\d{1,3}(?:\.\d{3})*,\d|-)'
PRODUCTION_KEYS = ('hydro', 'geothermal', 'solar', 'wind', 'bioenergy', 'total')
CONSUMPTION_LABELS = {'agriculture': 'AGRICOLTURA', 'industry': 'INDUSTRIA',
                      'services': 'SERVIZI|TERZIARIO', 'domestic': 'DOMESTICO', 'total': 'TOTALE'}


def read_row(text: str, label: str, columns: int) -> list[Decimal | None]:
    """Read one unambiguous row with the expected number of columns in GWh."""
    pattern = r'\s*(?:' + label + ')' + (r'[ \t]+(' + NUMBER + ')') * columns + r'[ \t]*'
    matches = [match for line in text.splitlines() if (match := re.fullmatch(pattern, line, re.I))]
    if len(matches) != 1:
        raise ValueError(f'Expected one {label} row with {columns} columns, found {len(matches)}')
    return [None if cell == '-' else Decimal(cell.replace('.', '').replace(',', '.')) for cell in matches[0].groups()]


def check_total(values: dict[str, Decimal | None], *, allow_dash: bool) -> dict[str, float | None]:
    """Preserve Terna's total and accept only differences consistent with one-decimal rounding."""
    total = values['total']
    parts = [value for key, value in values.items() if key != 'total']
    if total is None or (not allow_dash and None in parts):
        raise ValueError('Missing required electricity measurement')
    maximum_rounding = Decimal('0.05') * (1 + sum(value is not None for value in parts))
    if abs(total - sum(value for value in parts if value is not None)) > maximum_rounding:
        raise ValueError('Published total does not agree with its components')
    return {key: float(value) if value is not None else None for key, value in values.items()}


def read_report(year: int, report: dict, directory: Path) -> dict:
    """Extract the Campania tables from the exact pinned PDF edition."""
    import pymupdf

    path = directory / Path(urlsplit(report['url']).path).name
    with path.open('rb') as file:
        if file_digest(file, 'sha256').hexdigest() != report['sha256']:
            raise ValueError(f'Terna PDF differs from the reviewed edition: {path.name}')
    with pymupdf.open(path) as pdf:
        generation_page = pdf[report['generation_page'] - 1].get_text(sort=True)
        production_page = pdf[report['production_page'] - 1].get_text(sort=True)
        consumption_page = pdf[report['consumption_page'] - 1].get_text(sort=True)
    generation_heading = f'Tabella 5 - Produzione di energia elettrica per provincia - Anno {year}'
    production_heading = f'Tabella 6 - Produzione lorda rinnovabile per fonte e provincia - Anno {year}'
    consumption_heading = f'Tabella 7 - Consumi per provincia e classe merceologica - Anno {year}'
    if (generation_heading not in generation_page or production_heading not in production_page
            or consumption_heading not in consumption_page):
        raise ValueError(f'Expected provincial tables not found in {year}')
    generation = generation_page.partition(generation_heading)[2]
    production = production_page.partition(production_heading)[2].partition('Figura')[0]
    consumption = consumption_page.partition(consumption_heading)[2]
    if not re.search(r'GWh\s+Lorda\s+Ausiliari\s+Netta', generation, re.I):
        raise ValueError(f'Unexpected total generation column order in {year}')
    if not re.search(r'GWh\s+Idrica\s+Geotermica\s+Fotovoltaica\s+Eolica\s+Bioenergie\s+Totale', production, re.I):
        raise ValueError(f'Unexpected generation column order in {year}')
    if not re.search(r'GWh\s+Avellino\s+Benevento\s+Caserta\s+Napoli\s+Salerno\s+Campania', consumption, re.I):
        raise ValueError(f'Unexpected consumption column order in {year}')
    production_values = dict(zip(PRODUCTION_KEYS, read_row(production, 'Avellino', 6), strict=True))
    consumption_values = {key: read_row(consumption, label, 6)[0] for key, label in CONSUMPTION_LABELS.items()}
    gross, auxiliaries, net = read_row(generation, 'Avellino', 3)
    generation_values = check_total({'total': gross, 'auxiliaries': auxiliaries, 'net': net}, allow_dash=False)
    renewable_values = check_total(production_values, allow_dash=True)
    if generation_values['total'] < renewable_values['total']:
        raise ValueError(f'Renewable generation exceeds total generation in {year}')
    return {
        'year': year,
        'generation': {'gross': generation_values['total'], 'auxiliaries': generation_values['auxiliaries'],
                       'net': generation_values['net']},
        'production': renewable_values,
        'consumption': check_total(consumption_values, allow_dash=False),
        'source': {'url': report['url'], 'generationPage': report['generation_page'],
                   'productionPage': report['production_page'],
                   'consumptionPage': report['consumption_page'], 'sha256': report['sha256']},
    }


def collect(directory: Path) -> tuple[dict, dict]:
    """Build a complete series from the reports in the central registry."""
    source = load_scope()['provincial_publications']['energy']
    options = source['options']
    years = [read_report(int(year), report, directory) for year, report in sorted(options['reports'].items())]
    if not years:
        raise ValueError('No Terna reports configured')
    return {'version': 1, 'scope': '064', 'unit': 'GWh', 'years': years, 'rightsUrl': options['rights_url']}, source


def publish(document: dict, source: dict) -> str:
    """Append a complete revision and its import record in the same transaction."""
    checksum = semantic_checksum(document)
    years = document['years']
    with transaction() as db:
        require_current_schema(db)
        db.execute('SELECT pg_advisory_xact_lock(%s)', (PUBLICATION_LOCK,))
        previous = db.execute('SELECT checksum, document FROM atlas.energy_publications ORDER BY id DESC LIMIT 1').fetchone()
        if previous and previous[0] == checksum:
            return 'unchanged'
        if previous and {row['year'] for row in previous[1]['years']} - {row['year'] for row in years}:
            raise ValueError('Refusing an import that removes previously reviewed years')
        db.execute('INSERT INTO atlas.energy_publications(checksum,document) VALUES (%s,%s)', (checksum, Jsonb(document)))
        record_import(db, dataset_key=source['dataset_id'], source_name=source['publisher'], checksum=checksum,
                      status='success', source_url=source['landing_url'],
                      reference_period=f"{years[0]['year']}/{years[-1]['year']}", records_processed=len(years))
    return 'imported'


def stage_snapshot(directory: Path) -> None:
    """Extend a private local v2 snapshot copy with the latest verified database revision."""
    manifest_path = directory / 'manifest-v2.json'
    manifest = json.loads(manifest_path.read_text())
    if manifest.get('version') != 2 or not isinstance(manifest.get('entries'), dict):
        raise ValueError('Expected an existing v2 snapshot manifest')
    with transaction() as db:
        require_current_schema(db)
        row = db.execute('SELECT document FROM atlas.energy_publications ORDER BY id DESC LIMIT 1').fetchone()
    if not row:
        raise ValueError('Import the reviewed Terna series first')
    payload = gzip.compress(json.dumps(row[0], sort_keys=True, separators=(',', ':'), allow_nan=False).encode(), mtime=0)
    entry = {'bytes': len(payload), 'sha256': sha256(payload).hexdigest()}
    existing = manifest['entries'].get(OBJECT_NAME)
    if existing is not None and existing != entry:
        raise ValueError('Stage a revised series into a fresh copy of the base snapshot')
    with NamedTemporaryFile(dir=directory, delete_on_close=False) as file:
        file.write(payload)
        file.close()
        try:
            os.link(file.name, directory / OBJECT_NAME)
        except FileExistsError:
            if (directory / OBJECT_NAME).read_bytes() != payload:
                raise ValueError('A different energy object already exists in this snapshot')
    # The manifest is the visibility boundary. Write it only after the complete object exists.
    manifest['entries'][OBJECT_NAME] = entry
    with NamedTemporaryFile(dir=directory, delete_on_close=False) as file:
        file.write((json.dumps(manifest, indent=2) + '\n').encode())
        file.close()
        Path(file.name).replace(manifest_path)


def main() -> None:
    """Check source PDFs, import them into local Docker, or stage a private snapshot copy."""
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument('--pdf-dir', type=Path)
    inputs.add_argument('--snapshot-dir', type=Path)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.pdf_dir and args.check:
        document, _ = collect(args.pdf_dir)
        print(json.dumps(document, indent=2))
        return
    if args.check:
        parser.error('--check requires --pdf-dir')
    db_url = environment_value('DATABASE_URL', ROOT) or ''
    if urlsplit(db_url).hostname not in {'127.0.0.1', 'localhost'}:
        parser.error('Energy commands require the local Docker database')
    if args.snapshot_dir:
        stage_snapshot(args.snapshot_dir)
        print('Local energy snapshot staged.')
    else:
        document, source = collect(args.pdf_dir)
        print(publish(document, source))


if __name__ == '__main__':
    main()
