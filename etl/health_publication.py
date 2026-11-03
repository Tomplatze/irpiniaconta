"""Validate and publish a reviewed aggregate-only health snapshot."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from psycopg.types.json import Jsonb

from etl.database import PUBLICATION_LOCK, record_import, require_current_schema, semantic_checksum, transaction

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / 'data/health-publication.json'


def validate(document: dict) -> None:
    """Reject incomplete, unexpectedly granular or internally inconsistent publications."""
    expected = {'version', 'sources', 'series', 'causes', 'cancer', 'autism', 'survey', 'beds', 'admissions', 'staff'}
    if set(document) != expected or document['version'] != 1:
        raise ValueError('Unsupported or incomplete health publication')
    if any(set(item) != {'id', 'title', 'publisher', 'url', 'period', 'rights'} for item in document['sources']):
        raise ValueError('Unexpected source metadata')
    ids = {item['id'] for item in document['sources']}
    if len(ids) != len(document['sources']) or not all(item['url'].startswith('https://') for item in document['sources']):
        raise ValueError('Invalid or duplicated source citation')
    if set(document['series']) != {'01SAL001', '01SAL006', '01SAL020', '01SAL007'}:
        raise ValueError('Unexpected health series')
    for series in document['series'].values():
        if set(series) != {'Avellino', 'Campania', 'Italia'}:
            raise ValueError('Unexpected geographic scope')
        for points in series.values():
            if any(set(point) != {'year', 'value'} for point in points):
                raise ValueError('Unexpected series detail')
            years = [point['year'] for point in points]
            if not years or len(years) != len(set(years)) or years != sorted(years):
                raise ValueError('Duplicate or unordered years')
            if any(not isinstance(p['value'], (int, float)) or not math.isfinite(p['value']) for p in points):
                raise ValueError('Invalid series value')
    if {item['code'] for item in document['causes']} != {'2', '4_1', '5', '6', '7', '8_3'}:
        raise ValueError('Unexpected death categories')
    for cause in document['causes']:
        if set(cause) != {'code', 'name', 'points'} or any(set(p) != {'year', 'value'} for p in cause['points']):
            raise ValueError('Unexpected cause detail')
        if [p['year'] for p in cause['points']] != list(range(2018, 2024)):
            raise ValueError('Unexpected death series period')
        if any(not isinstance(p['value'], int) or p['value'] < 100 for p in cause['points']):
            raise ValueError('Suppressed or small death count')
    if {group['label'] for group in document['cancer']} != {'Maschi', 'Femmine'}:
        raise ValueError('Unexpected cancer breakdown')
    allowed_cancer = {'Maschi': {'Prostata', 'Polmone', 'Colon e retto', 'Vescica, tumori maligni', 'Stomaco'},
                      'Femmine': {'Mammella', 'Colon e retto', 'Tiroide', 'Utero, corpo', 'Polmone'}}
    for group in document['cancer']:
        if set(group) != {'label', 'entries'} or {entry['name'] for entry in group['entries']} != allowed_cancer[group['label']]:
            raise ValueError('Unexpected cancer sites')
        if any(set(entry) != {'name', 'value', 'low', 'high'} for entry in group['entries']):
            raise ValueError('Unexpected cancer detail')
        if len(group['entries']) != 5 or any(not (0 <= e['low'] <= e['value'] <= e['high']) for e in group['entries']):
            raise ValueError('Invalid cancer confidence intervals')
    shapes = {'autism': {'value', 'source', 'period'}, 'survey': {'value', 'low', 'high', 'source', 'period'},
              'beds': {'total', 'year', 'source', 'byType', 'byRegime', 'byProvider'},
              'admissions': {'total', 'year', 'source'}, 'staff': {'total', 'year', 'source', 'physicians', 'nurses', 'roles'}}
    for key, fields in shapes.items():
        if set(document[key]) != fields:
            raise ValueError('Unexpected aggregate detail')
    for key in ('autism', 'survey', 'beds', 'admissions', 'staff'):
        if document[key]['source'] not in ids:
            raise ValueError('Missing source citation')
    allowed_beds = {'byType': {'Acuti', 'Riabilitazione', 'Lungodegenza'},
                    'byRegime': {'Degenza ordinaria', 'Day hospital', 'Day surgery', 'Degenza a pagamento'},
                    'byProvider': {'Azienda ospedaliera', 'Ospedali a gestione diretta', 'Case di cura private accreditate'}}
    for key in ('byType', 'byRegime', 'byProvider'):
        if {x['name'] for x in document['beds'][key]} != allowed_beds[key]:
            raise ValueError('Unexpected bed categories')
        if any(set(x) != {'name', 'value'} for x in document['beds'][key]):
            raise ValueError('Unexpected bed breakdown detail')
        if sum(x['value'] for x in document['beds'][key]) != document['beds']['total']:
            raise ValueError('Bed breakdown does not add to total')
    if {x['name'] for x in document['staff']['roles']} != {'Sanitario', 'Tecnico', 'Amministrativo', 'Professionale', 'Non classificato'}:
        raise ValueError('Unexpected staff categories')
    if any(set(x) != {'name', 'value'} for x in document['staff']['roles']):
        raise ValueError('Unexpected staffing detail')
    if sum(x['value'] for x in document['staff']['roles']) != document['staff']['total']:
        raise ValueError('Staff breakdown does not add to total')
    if not document['survey']['low'] <= document['survey']['value'] <= document['survey']['high']:
        raise ValueError('Invalid survey interval')


def publish(path: Path = SNAPSHOT, connection=None, *, allow_revision: bool = True) -> dict:
    """Append a whole validated snapshot under the common publication lock."""
    document = json.loads(path.read_text())
    validate(document)
    checksum = semantic_checksum(document)
    with transaction(connection) as database:
        require_current_schema(database)
        database.execute('SELECT pg_advisory_xact_lock(%s)', (PUBLICATION_LOCK,))
        last = database.execute('SELECT checksum FROM atlas.health_publications ORDER BY id DESC LIMIT 1').fetchone()
        if last and last[0] == checksum:
            return {'status': 'unchanged', 'checksum': checksum}
        if last and not allow_revision:
            raise ValueError('Refusing seed: current health publication differs from the snapshot')
        database.execute('INSERT INTO atlas.health_publications(checksum,document) VALUES (%s,%s)', (checksum, Jsonb(document)))
        record_import(database, dataset_key='health-publication', source_name='Reviewed health snapshot',
                      checksum=checksum, status='success', records_processed=sum(len(points) for series in document['series'].values() for points in series.values()))
    return {'status': 'published', 'checksum': checksum}


def main() -> None:
    """Support a non-mutating validation before publication."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--file', type=Path, default=SNAPSHOT)
    args = parser.parse_args()
    if args.check:
        document = json.loads(args.file.read_text())
        validate(document)
        print(json.dumps({'status': 'valid', 'checksum': semantic_checksum(document)}))
    else:
        print(json.dumps(publish(args.file)))


if __name__ == '__main__':
    main()
