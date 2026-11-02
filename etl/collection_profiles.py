"""Inspect source-level records without promoting them to public indicators.

Staging retains original fields and source missingness. Geographic coverage means
that at least one record was found, not that an inventory is exhaustive.
"""
from __future__ import annotations

from collections import Counter
from contextlib import contextmanager
import csv
import gzip
import io
import json
import math
from pathlib import Path
import re
from typing import Iterator
import xml.etree.ElementTree as ET
from zipfile import ZipFile

from openpyxl import load_workbook
from etl.adapters.municipal_keys import cadastral_crosswalk, normalized_name


class Geography:
    """Resolve only exact official codes or uniquely normalized official names."""

    def __init__(self, municipalities: list[dict[str, str]], registry: Path):
        self.codes = {item['code'] for item in municipalities}
        self.names = {normalized_name(item['name']): item['code'] for item in municipalities}
        if len(self.names) != len(self.codes):
            raise ValueError('Ambiguous official municipal names')
        self.cadastral = cadastral_crosswalk(registry, self.codes)
        self.stations: dict[str, str] = {}
        self.authorities: dict[str, str] = {}
        self.bdap_codes: dict[str, str] = {}
        self.projects: dict[tuple[str, str], set[str]] = {}
        self.buildings: dict[str, str] = {}
        self.civitas: dict[str, str] = {}

    def resolve(self, row: dict[str, object], job: dict[str, object]) -> list[str]:
        """Apply a declared source-specific key rule; never truncate arbitrary codes."""
        rule = str(job['key_rule'])
        column = str(job.get('key_column', ''))
        value = str(row.get(column, '')).strip()
        code: str | None = None
        if rule == 'istat':
            code = value.zfill(6) if re.fullmatch(r'\d{1,6}', value) else None
        elif rule == 'waste':
            code = value[2:] if re.fullmatch(r'15064\d{3}', value) else None
        elif rule == 'bdap':
            if str(row.get('Codice Tipologia Soggetto', '')).strip() != 'ELCOMU':
                return []
            province = str(row.get('Codice Provincia', '')).strip().zfill(3)
            code = province + value.zfill(3) if province == '064' and re.fullmatch(r'\d{1,3}', value) else None
        elif rule == 'opencoesione':
            # The extended export uses region(3)+province(3)+municipality(3).
            values = [part.strip() for part in re.split(r'[;,|]', value)]
            return sorted({part[3:] for part in values if re.fullmatch(r'015064\d{3}', part) and part[3:] in self.codes})
        elif rule == 'cadastral':
            code = self.cadastral.get(value)
        elif rule == 'name':
            code = self.names.get(normalized_name(value))
        elif rule == 'station':
            code = self.stations.get(value)
        elif rule == 'pnrr_location':
            province = str(row.get('Provincia', '')).strip().zfill(3)
            code = province + value.zfill(3) if province == '064' and re.fullmatch(r'\d{1,3}', value) else None
        elif rule == 'pnrr_project':
            return sorted(self.projects.get((str(row.get('CUP', '')), str(row.get('Codice Locale Progetto', ''))), set()))
        elif rule == 'building':
            code = self.buildings.get(value)
        elif rule == 'bdap_identity':
            code = self.bdap_codes.get(value)
        elif rule == 'authority_fiscal':
            # MEF CSV encloses fiscal identifiers in brackets to preserve zeros.
            identifier = value[1:-1] if value.startswith('[') and value.endswith(']') else value
            code = self.authorities.get(identifier) if re.fullmatch(r'\d{11}', identifier) else None
        elif rule == 'civitas':
            code = self.civitas.get(value)
        elif rule == 'anac':
            location = str(row.get('luogo_istat', '')).strip()
            authority = self.authorities.get(str(row.get('cf_amministrazione_appaltante', '')).strip())
            row['_authority_municipality_code'] = authority
            row['_contract_location_municipality_code'] = location if location in self.codes else None
            return sorted({key for key in [authority, location] if key in self.codes})
        elif rule == 'none':
            return []
        else:
            raise ValueError(f'Unknown geographic key rule: {rule}')
        return [code] if code in self.codes else []


class Sink:
    """Stream selected source rows to a compressed, inspectable staging file."""

    def __init__(self, output: Path, codes: set[str]):
        self.output = output
        self.expected_codes = codes
        self.covered: set[str] = set()
        self.periods: Counter[str] = Counter()
        self.tables: dict[str, dict[str, object]] = {}
        self.unmatched: Counter[str] = Counter()
        self.selected_rows = 0
        self.scanned_rows = 0
        self.null_cells = 0
        self.sentinel_cells = 0
        self._file = gzip.open(output, 'wt', encoding='utf-8')

    def add(self, table: str, row: dict[str, object], codes: list[str], period: str, *, context_only: bool = False):
        """Retain one source row once, including its multiple municipal associations."""
        self.scanned_rows += 1
        stats = self.tables.setdefault(table, {'scanned_rows': 0, 'selected_rows': 0, 'fields': list(row)})
        stats['scanned_rows'] += 1
        if not codes and not context_only:
            return
        stats['selected_rows'] += 1
        self.selected_rows += 1
        self.covered.update(codes)
        if period:
            self.periods[period] += 1
        self.null_cells += sum(value is None or str(value).strip() in ('', '-', 'n.d.') for value in row.values())
        self.sentinel_cells += sum(str(value).strip() in ('-9999', '-9999.0') for value in row.values())
        self._file.write(json.dumps({'table': table, 'municipality_codes': codes, 'period': period,
                                     'source': row}, ensure_ascii=False, allow_nan=False) + '\n')

    def close(self) -> dict[str, object]:
        """Return coverage and quality evidence, not an assertion of completeness."""
        self._file.close()
        return {'scanned_rows': self.scanned_rows, 'selected_rows': self.selected_rows,
                'covered_municipalities': len(self.covered), 'municipality_codes': sorted(self.covered),
                'missing_municipality_codes': sorted(self.expected_codes - self.covered),
                'periods': sorted(self.periods), 'rows_by_period': dict(sorted(self.periods.items())),
                'tables': self.tables, 'source_blank_or_null_cells': self.null_cells,
                'source_minus_9999_cells': self.sentinel_cells,
                'unmatched_in_scope': dict(self.unmatched), 'staging_file': str(self.output)}


def category_codes(category: dict[str, object], size: int) -> list[str]:
    """Validate JSON-stat category positions rather than assuming dictionary order."""
    index = category['index']
    codes = list(index) if isinstance(index, list) else [code for code, _ in sorted(index.items(), key=lambda item: item[1])]
    positions = list(range(size)) if isinstance(index, list) else sorted(index.values())
    if len(codes) != size or positions != list(range(size)):
        raise ValueError('Invalid JSON-stat category index')
    return codes


def jsonstat(path: Path, job: dict[str, object], geo: Geography, sink: Sink) -> dict[str, object]:
    """Decode sparse JSON-stat values while retaining every dimension and flag."""
    data = json.loads(path.read_text())
    dimensions, sizes = data['id'], data['size']
    if not dimensions:
        return {'empty_response': True, 'dimensions': {}, 'potential_cells': 0}
    if len(dimensions) != len(sizes) or 'REF_AREA' not in dimensions:
        raise ValueError('Expected municipal JSON-stat dimensions')
    categories = {name: category_codes(data['dimension'][name]['category'], sizes[i]) for i, name in enumerate(dimensions)}
    if set(categories['REF_AREA']) - geo.codes:
        raise ValueError('Unexpected geography returned by a municipal query')
    values = data.get('value', {})
    items = enumerate(values) if isinstance(values, list) else ((int(key), value) for key, value in values.items())
    potential = math.prod(sizes)
    flags = data.get('status', {})
    numeric = 0
    for flat_index, value in items:
        if flat_index < 0 or flat_index >= potential:
            raise ValueError('JSON-stat value index outside dimensions')
        remaining = flat_index
        indexes: list[int] = []
        for size in reversed(sizes):
            indexes.append(remaining % size)
            remaining //= size
        record = {name: categories[name][position] for name, position in zip(dimensions, reversed(indexes))}
        record['value'] = value
        record['source_status'] = flags[flat_index] if isinstance(flags, list) and flat_index < len(flags) else flags.get(str(flat_index)) if isinstance(flags, dict) else None
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            numeric += 1
        sink.add('observations', record, [record['REF_AREA']], record.get('TIME_PERIOD', ''))
    metadata_path = sink.output.with_name(sink.output.name.replace('.rows.jsonl.gz', '.dimensions.json'))
    metadata_path.write_text(json.dumps({'id': dimensions, 'size': sizes, 'dimension': data['dimension'],
                                        'extension': data.get('extension'), 'role': data.get('role')}, ensure_ascii=False, indent=2) + '\n')
    return {'dimensions': {name: {'size': sizes[i], 'codes': categories[name]} for i, name in enumerate(dimensions)},
            'potential_cells': potential, 'numeric_cells': numeric,
            'absent_or_null_cells': potential - numeric, 'dimension_metadata_file': str(metadata_path)}


def unique_headers(raw: list[str]) -> list[str]:
    """Keep duplicate and trailing anonymous fields without overwriting values."""
    used: Counter[str] = Counter()
    result = []
    for position, value in enumerate(raw):
        name = value.strip() or f'_unnamed_{position + 1}'
        used[name] += 1
        result.append(name if used[name] == 1 else f'{name}__{used[name]}')
    return result


def csv_rows(handle: io.TextIOBase, delimiter: str, skip: int, *, waste_aggregations: bool = False,
             required: set[str] | None = None, trailing_unlabelled_blanks: bool = False) -> Iterator[dict[str, object]]:
    """Read strict CSV, preserving original strings and explicit empty cells."""
    csv.field_size_limit(8_000_000)
    reader = csv.reader(handle, delimiter=delimiter)
    for _ in range(skip):
        next(reader)
    raw_headers = next(reader)
    if trailing_unlabelled_blanks:
        while raw_headers and not raw_headers[-1].strip():
            raw_headers.pop()
    headers = unique_headers(raw_headers)
    if required and not required.issubset(headers):
        raise ValueError(f'CSV schema missing declared columns: {sorted(required - set(headers))}')
    for values in reader:
        if not values or not any(value.strip() for value in values):
            continue
        if waste_aggregations and len(values) == 1 and values[0].startswith('Note: '):
            continue  # Publisher footer, not a municipal observation.
        trailing_count = 0
        if trailing_unlabelled_blanks:
            while len(values) > len(headers) and not values[-1].strip():
                values.pop()
                trailing_count += 1
        if len(values) == len(headers) + 1 and values[-1] == '':
            values.pop()  # ISPRA appends a delimiter after the final field.
        omitted: list[str] = []
        if waste_aggregations and len(values) < len(headers) and len(values) > 5 and values[5].startswith('Vedi aggregazione:'):
            omitted = headers[len(values):]
            values.extend([None] * (len(headers) - len(values)))
        if len(values) != len(headers):
            raise ValueError(f'CSV row shape mismatch: {len(values)} != {len(headers)}')
        record = dict(zip(headers, values))
        if omitted:
            record['_source_omitted_fields'] = omitted
        if trailing_count:
            record['_source_trailing_unlabelled_empty_cells'] = trailing_count
        yield record


@contextmanager
def csv_sources(path: Path, job: dict[str, object]):
    """Stream CSV members directly from a ZIP; do not extract arbitrary paths."""
    if path.suffix == '.zip':
        with ZipFile(path) as archive:
            names = [name for name in archive.namelist() if name.lower().endswith('.csv') and '__MACOSX' not in name
                     and (not job.get('member') or name == job['member'])]
            if not names:
                raise ValueError('ZIP contains no CSV tables')
            yield [(name, lambda name=name: archive.open(name)) for name in names]
    else:
        yield [(path.name, lambda: path.open('rb'))]


def csv_profile(path: Path, job: dict[str, object], geo: Geography, sink: Sink) -> dict[str, object]:
    """Filter records with declared keys while retaining all original variables."""
    variables: set[str] = set()
    with csv_sources(path, job) as tables:
        for name, open_stream in tables:
            with open_stream() as binary:
                with io.TextIOWrapper(binary, encoding=str(job.get('encoding', 'utf-8-sig')), errors='strict', newline='') as handle:
                    required = set(job.get('required_columns', [])) | set(job.get('filters', {}))
                    if job.get('key_column'):
                        required.add(str(job['key_column']))
                    if job['key_rule'] == 'pnrr_project':
                        required.update(['CUP', 'Codice Locale Progetto'])
                    if job.get('period_column'):
                        required.add(str(job['period_column']))
                    for row in csv_rows(handle, str(job.get('delimiter', ',')), int(job.get('skip_rows', 0)), waste_aggregations=bool(job.get('waste_aggregations')), required=required, trailing_unlabelled_blanks=bool(job.get('trailing_unlabelled_blanks'))):
                        if any(str(row.get(key, '')).strip().casefold() != str(value).casefold() for key, value in job.get('filters', {}).items()):
                            continue
                        codes = geo.resolve(row, job)
                        if codes and job.get('variable_column'):
                            variables.add(str(row[str(job['variable_column'])]))
                        if job.get('require_match') and not codes:
                            sink.unmatched[str(row.get(str(job['key_column']), ''))] += 1
                        period = str(row.get(str(job.get('period_column', '')), job.get('period', ''))).strip()
                        if period and job.get('period_format'):
                            from datetime import datetime
                            period = datetime.strptime(period, str(job['period_format'])).date().isoformat()
                        sink.add(name, row, codes, period, context_only=bool(job.get('context_only')))
    return {'key_rule': job['key_rule'], 'encoding': job.get('encoding', 'utf-8-sig'), 'source_variables': sorted(variables)}


def sections(path: Path, job: dict[str, object], geo: Geography, sink: Sink) -> dict[str, object]:
    """Inspect 2023 census sections with all variables and original section keys."""
    with ZipFile(path) as archive:
        workbook = load_workbook(io.BytesIO(archive.read(str(job['member']))), read_only=True, data_only=True)
        try:
            rows = workbook.active.iter_rows(values_only=True)
            headers = unique_headers([str(value or '') for value in next(rows)])
            for values in rows:
                row = dict(zip(headers, values))
                codes = geo.resolve(row, {'key_rule': 'istat', 'key_column': 'PROCOM'})
                sink.add(workbook.active.title, row, codes, '2023')
        finally:
            workbook.close()
        dictionary = load_workbook(io.BytesIO(archive.read(str(job['dictionary_member']))), read_only=True, data_only=True)
        try:
            definitions = list(dictionary.active.iter_rows(values_only=True))
        finally:
            dictionary.close()
    dictionary_path = sink.output.with_name(sink.output.name.replace('.rows.jsonl.gz', '.dictionary.json'))
    dictionary_path.write_text(json.dumps(definitions, ensure_ascii=False, indent=2) + '\n')
    return {'grain': 'Census section', 'dictionary_file': str(dictionary_path)}


def aci_vehicles(path: Path, job: dict[str, object], geo: Geography, sink: Sink) -> dict[str, object]:
    """Decode the source ODS municipal sheet, including grouped geography cells."""
    ns = {'t': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0', 'x': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
          'o': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0'}
    with ZipFile(path) as outer:
        nested = next(name for name in outer.namelist() if name.endswith('/Parco veicoli 2024 OD.zip'))
        with ZipFile(io.BytesIO(outer.read(nested))) as inner:
            member = next(name for name in inner.namelist() if name.endswith('/Parco_veicolare_2024.ods'))
            with ZipFile(io.BytesIO(inner.read(member))) as ods:
                root = ET.fromstring(ods.read('content.xml'))
    table = next(item for item in root.findall('.//t:table', ns) if item.attrib.get(f"{{{ns['t']}}}name") == '45_Comune_categoria')
    headers: list[str] = []
    carry = ['', '', '']
    for position, item in enumerate(table.findall('t:table-row', ns)):
        cells: list[object] = []
        for cell in item:
            text = ' '.join(''.join(element.itertext()) for element in cell.findall('x:p', ns))
            value: object = cell.attrib.get(f"{{{ns['o']}}}value", text)
            repeated = int(cell.attrib.get(f"{{{ns['t']}}}number-columns-repeated", '1'))
            cells.extend([value] * min(repeated, max(0, 16 - len(cells))))
            if len(cells) >= 16:
                break
        if position == 2:
            headers = unique_headers([str(value) for value in cells])
            if headers[:4] != ['Area Geografica', 'Regione', 'Provincia', 'Comune']:
                raise ValueError('ACI municipal sheet schema changed')
            continue
        if position < 3 or len(cells) < 4 or not str(cells[3]).strip():
            continue
        for index in range(3):
            if cells[index]:
                carry[index] = str(cells[index])
            cells[index] = carry[index]
        row = dict(zip(headers, cells))
        if normalized_name(str(row['Provincia'])) != 'avellino':
            continue
        codes = geo.resolve(row, {'key_rule': 'name', 'key_column': 'Comune'})
        if not codes:
            sink.unmatched[str(row['Comune'])] += 1
        sink.add('45_Comune_categoria', row, codes, '2024')
    return {'grain': 'Municipality / vehicle category', 'numeric_strings': 'ODS office:value; blanks retained'}


def json_rows(path: Path, job: dict[str, object], geo: Geography, sink: Sink) -> dict[str, object]:
    """Profile declared JSON row collections without interpreting their values."""
    data = json.loads(path.read_text())
    for key in str(job.get('rows_path', '')).split('.'):
        if key:
            data = data[key]
    if job.get('single_object') and isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise ValueError('Expected an array of source records')
    for row in data:
        if not isinstance(row, dict):
            raise ValueError('Source row is not an object')
        codes = geo.resolve(row, job)
        sink.add('records', row, codes, str(row.get(str(job.get('period_column', '')), job.get('period', 'undated'))))
    return {'key_rule': job['key_rule']}


def mic_places(path: Path, job: dict[str, object], geo: Geography, sink: Sink) -> dict[str, object]:
    """Resolve cultural sites through their explicit JSON-LD site/address graph."""
    data = json.loads(path.read_text())
    nodes = {node['@id']: node for node in data['@graph']}
    for place in nodes.values():
        if place.get('@type') != 'cis:CulturalInstituteOrSite':
            continue
        sites = place.get('cis:hasSite', [])
        sites = sites if isinstance(sites, list) else [sites]
        codes: set[str] = set()
        related = {}
        for reference in sites:
            site = nodes.get(reference['@id'], {})
            address = nodes.get(site.get('cis:siteAddress', {}).get('@id', ''), {})
            city = nodes.get(address.get('clvapit:hasCity', {}).get('@id', ''), {})
            province = address.get('clvapit:hasProvince', {}).get('@id', '')
            if not province.endswith('/Avellino'):
                continue
            label = city.get('l0:name', city.get('rdfs:label', ''))
            name = label.get('@value', '') if isinstance(label, dict) else str(label)
            if not name:
                from urllib.parse import unquote
                name = unquote(address.get('clvapit:hasCity', {}).get('@id', '').rsplit('/', 1)[-1]).replace('_', ' ')
            resolved = geo.resolve({'name': name}, {'key_rule': 'name', 'key_column': 'name'})
            if not resolved:
                sink.unmatched[name] += 1
            codes.update(resolved)
            related.update({node['@id']: node for node in [site, address, city] if '@id' in node})
        sink.add('cultural_sites', {'place': place, 'related_geography': related}, sorted(codes), 'undated_source_records')
    return {'graph_node_count': len(nodes), 'record_date': 'Distribution checked now; individual record freshness not supplied',
            'context': data.get('@context'), 'media_policy': 'Media URLs retained as source fields; no photos downloaded'}


def tourism(path: Path, job: dict[str, object], geo: Geography, sink: Sink) -> dict[str, object]:
    """Flatten declared multi-row XLSX headers without merging source totals."""
    with ZipFile(path) as archive:
        member = next(name for name in archive.namelist() if name.endswith('.xlsx'))
        workbook = load_workbook(io.BytesIO(archive.read(member)), read_only=True, data_only=True)
        try:
            sheet = workbook.active
            rows = sheet.iter_rows(values_only=True)
            header_rows = [next(rows) for _ in range(6)]
            leaf = header_rows[5]
            headers: list[str] = []
            group = ''
            for index, value in enumerate(leaf):
                if index >= 8 and header_rows[4][index]:
                    group = str(header_rows[4][index]).strip()
                headers.append(str(value).strip() if index < 8 else f'{group}: {str(value).strip()}' if value else f'_unused_{index + 1}')
            headers = unique_headers(headers)
            key_column = 'Cod. Istat'
            if key_column not in headers or 'Anno/Year' not in headers:
                raise ValueError('Tourism workbook schema changed')
            omitted_legacy: Counter[str] = Counter()
            for values in rows:
                row = dict(zip(headers, values))
                codes = geo.resolve(row, {'key_rule': 'istat', 'key_column': key_column})
                if str(row.get(key_column, '')).startswith('064') and not codes:
                    omitted_legacy[str(row[key_column])] += 1
                sink.add(sheet.title, row, codes, str(row['Anno/Year']))
        finally:
            workbook.close()
    return {'header_rows': [list(row) for row in header_rows], 'unmerged_historical_municipal_codes': dict(omitted_legacy),
            'notes': 'Historic source codes kept; no silent merging of former Montoro municipalities into current geography.'}


def historical_agriculture(path: Path, job: dict[str, object], geo: Geography, sink: Sink) -> dict[str, object]:
    """Stream the code-only historical export; skip redundant 39 GB descriptions."""
    legacy: Counter[str] = Counter()
    source_rows = 0
    with ZipFile(path) as archive:
        member = next(name for name in archive.namelist() if 'DATI SOLO CODICI' in name and name.endswith('.csv'))
        labelled = next(name for name in archive.namelist() if name.endswith('-data-en.csv'))
        with archive.open(labelled) as labelled_handle:
            wide = next(csv.reader([labelled_handle.readline().decode('utf-8-sig')], delimiter='|'))
        headers = unique_headers(wide[:-2:2] + wide[-2:])
        if headers[0] != 'ITTER107' or 'TIME' not in headers or headers[-2:] != ['Value', 'Flags']:
            raise ValueError('Historical agriculture labelled header schema changed')
        with archive.open(member) as handle:
            for line in handle:
                if not line.strip():
                    continue
                source_rows += 1
                if not line.startswith(b'064'):
                    continue
                values = next(csv.reader([line.decode('utf-8')], delimiter='|'))
                if len(values) != len(headers):
                    raise ValueError('Historical agriculture row shape mismatch')
                row = dict(zip(headers, values))
                codes = geo.resolve(row, {'key_rule': 'istat', 'key_column': 'ITTER107'})
                if not codes:
                    legacy[row['ITTER107']] += 1
                sink.add('historical_agriculture_code_table', row, codes, row['TIME'])
        dictionaries = {}
        for name in archive.namelist():
            if name.startswith('METADATA/') and name.endswith('.csv'):
                payload = archive.read(name)
                text = payload.decode('utf-16' if payload.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8-sig')
                delimiter = '\t' if '\t' in text.splitlines()[0] else '|'
                dictionaries[name] = list(csv.reader(io.StringIO(text), delimiter=delimiter))
    dictionary_path = sink.output.with_name(sink.output.name.replace('.rows.jsonl.gz', '.dictionary.json'))
    dictionary_path.write_text(json.dumps(dictionaries, ensure_ascii=False, indent=2) + '\n')
    return {'national_code_table_rows': source_rows, 'unmerged_legacy_code_rows': dict(legacy),
            'dictionary_file': str(dictionary_path), 'national_member_bytes': archive.getinfo(member).file_size,
            'notes': 'Only exact current municipal codes selected; original historical geography not converted. Code-only table scanned to EOF/CRC. Redundant English/Italian descriptions retained in the raw archive, not decompressed.'}


def cultural_bindings(path: Path, job: dict[str, object], geo: Geography, sink: Sink) -> dict[str, object]:
    """Retain RDF location relations, including historical and shooting roles."""
    data = json.loads(path.read_text())
    if not {'property', 'type', 'cityLabel', 'location'}.issubset(data.get('head', {}).get('vars', [])):
        raise ValueError('ArCo SPARQL result schema changed')
    bindings = data['results']['bindings']
    if len(bindings) != job['expected_count']:
        raise ValueError('ArCo result count differs from independent query count')
    for binding in bindings:
        row = {key: value['value'] for key, value in binding.items()}
        row['_rdf_bindings'] = binding
        codes = geo.resolve(row, {'key_rule': 'name', 'key_column': 'cityLabel'})
        sink.add('cultural_property_location_relations', row, codes, 'undated_catalog_relations')
    return {'source_relation_count': len(bindings), 'notes': 'Location roles are retained. Shooting/collecting locations are not evidence of current property storage; rows are relations, not unique cultural-property counts.'}


def provincial_business_report(path: Path, job: dict[str, object], geo: Geography, sink: Sink) -> dict[str, object]:
    """Read the actual annual report table without inventing municipal detail."""
    namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    with ZipFile(path) as archive:
        root = ET.fromstring(archive.read('word/document.xml'))
    matched = []
    for table_index, table in enumerate(root.findall('.//w:tbl', namespace)):
        # OpenXML contains formatting whitespace: only w:t nodes are data.
        rows = [
            [''.join(text.text or '' for text in cell.findall('.//w:t', namespace)).strip()
             for cell in row.findall('w:tc', namespace)] for row in table.findall('w:tr', namespace)]
        header = next((row for row in rows if 'PROVINCE' in row and 'Iscrizioni' in row), None)
        if not header:
            continue
        for row in rows:
            for index, value in enumerate(row):
                if value == 'AVELLINO':
                    if len(row) != len(header) or header[index] != 'PROVINCE' or index + 5 > len(row):
                        raise ValueError('Movimprese provincial table shape changed')
                    record = dict(zip(unique_headers(header[index:index + 5]), row[index:index + 5]))
                    record['_source_table_index'] = table_index
                    matched.append(record)
    if len(matched) != 1:
        raise ValueError('Expected one Avellino provincial annual report row')
    sink.add('provincial_annual_business_demography', matched[0], [], str(job['period']), context_only=True)
    return {'grain': 'Province', 'notes': 'Registrations, closures, balance and growth in the official annual Movimprese report. Not municipal business counts or company registry records.'}


def profile(path: Path, job: dict[str, object], geo: Geography, output: Path, *, raw_root: Path | None = None) -> dict[str, object]:
    """Dispatch a declared profiler and remove incomplete output on failure."""
    sink = Sink(output, geo.codes)
    try:
        handlers = {'jsonstat': jsonstat, 'csv': csv_profile, 'sections': sections, 'aci': aci_vehicles,
                    'json_rows': json_rows, 'mic': mic_places, 'tourism': tourism, 'historical_agri': historical_agriculture,
                    'cultural_bindings': cultural_bindings, 'movimprese': provincial_business_report}
        if str(job['handler']) in ('boundaries', 'geojson', 'weather', 'natura', 'osm', 'events', 'esri_lines'):
            from etl.collection_spatial import official_boundaries, geojson, weather, natura, osm, events, esri_lines
            handlers.update({'boundaries': official_boundaries, 'geojson': geojson, 'weather': weather,
                             'natura': natura, 'osm': osm, 'events': events, 'esri_lines': esri_lines})
        result = handlers[str(job['handler'])](path, job, geo, sink)
        if job.get('field_dictionary_file'):
            dictionary = load_workbook((raw_root or Path(__file__).resolve().parents[1] / 'data/raw') / Path(str(job['field_dictionary_file'])).relative_to('data/raw'), read_only=True, data_only=True)
            try:
                sheets = {}
                for sheet in dictionary:
                    sheet.reset_dimensions()
                    sheets[sheet.title] = [list(row) for row in sheet.iter_rows(values_only=True)]
            finally:
                dictionary.close()
            dictionary_path = output.with_name(output.name.replace('.rows.jsonl.gz', '.dictionary.json'))
            dictionary_path.write_text(json.dumps(sheets, ensure_ascii=False, indent=2) + '\n')
            result['dictionary_file'] = str(dictionary_path)
        return {**sink.close(), **result}
    except Exception:
        sink._file.close()
        output.unlink(missing_ok=True)
        raise
