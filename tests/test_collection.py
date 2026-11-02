"""Meaningful source-quality regression tests using explicit synthetic fixtures."""
import gzip
import io
import json
from pathlib import Path
import tempfile
import unittest

from etl.collection_profiles import Geography, csv_rows, profile


def test_geography():
    """Build a small, clearly synthetic geographic fixture independent of raw data."""
    geo = Geography.__new__(Geography)
    geo.codes = {'064001', '064002'}
    geo.names = {'fixtureone': '064001', 'fixturetwo': '064002'}
    geo.cadastral = {'A001': '064001'}
    geo.authorities = {'00000000001': '064001'}
    geo.stations = {'FIXTURE': '064002'}
    geo.projects = {('TEST_CUP', 'TEST_LOCAL'): {'064001', '064002'}}
    geo.buildings = {}
    geo.civitas = {}
    return geo


class GeographicKeys(unittest.TestCase):
    def test_bracketed_mef_fiscal_keys_preserve_leading_zeros(self):
        rule = {'key_rule': 'authority_fiscal', 'key_column': 'fiscal'}
        self.assertEqual(test_geography().resolve({'fiscal': '[00000000001]'}, rule), ['064001'])
        self.assertEqual(test_geography().resolve({'fiscal': '1'}, rule), [])

    def test_region_province_prefixes_are_not_arbitrarily_truncated(self):
        geo = test_geography()
        self.assertEqual(geo.resolve({'id': '15064001'}, {'key_rule': 'waste', 'key_column': 'id'}), ['064001'])
        self.assertEqual(geo.resolve({'id': '99064001'}, {'key_rule': 'waste', 'key_column': 'id'}), [])

    def test_bdap_authority_type_not_physical_location(self):
        geo = test_geography()
        row = {'Codice Provincia': '64', 'Codice Comune': '1', 'Codice Tipologia Soggetto': 'ELCOMU'}
        self.assertEqual(geo.resolve(row, {'key_rule': 'bdap', 'key_column': 'Codice Comune'}), ['064001'])
        row['Codice Tipologia Soggetto'] = 'OTHER_AUTHORITY'
        self.assertEqual(geo.resolve(row, {'key_rule': 'bdap', 'key_column': 'Codice Comune'}), [])

    def test_multilocation_project_is_one_row_with_distinct_associations(self):
        geo = test_geography()
        self.assertEqual(geo.resolve({'COD_COMUNE': '015064001;015064002;015064001'},
                                    {'key_rule': 'opencoesione', 'key_column': 'COD_COMUNE'}), ['064001', '064002'])
        self.assertEqual(geo.resolve({'CUP': 'TEST_CUP', 'Codice Locale Progetto': 'WRONG_LOCAL'},
                                    {'key_rule': 'pnrr_project'}), [])

    def test_contract_authority_and_place_remain_distinct(self):
        row = {'luogo_istat': '064002', 'cf_amministrazione_appaltante': '00000000001'}
        self.assertEqual(test_geography().resolve(row, {'key_rule': 'anac', 'key_column': 'luogo_istat'}), ['064001', '064002'])
        self.assertEqual(row['_authority_municipality_code'], '064001')
        self.assertEqual(row['_contract_location_municipality_code'], '064002')


class SourceRows(unittest.TestCase):
    def test_html_response_cannot_pass_as_csv(self):
        with self.assertRaisesRegex(ValueError, 'missing declared columns'):
            list(csv_rows(io.StringIO('<html>Rejected</html>\n'), ',', 0, required={'municipal_code'}))

    def test_nonempty_extra_fields_are_not_discarded(self):
        with self.assertRaisesRegex(ValueError, 'shape mismatch'):
            list(csv_rows(io.StringIO('code;value\n064001;2;UNEXPECTED\n'), ';', 0, trailing_unlabelled_blanks=True))

    def test_mef_blank_separators_do_not_shift_named_variables(self):
        rows = list(csv_rows(io.StringIO('code;value\n064001;; ;\n'), ';', 0, trailing_unlabelled_blanks=True))
        self.assertEqual(rows[0]['value'], '')
        self.assertEqual(rows[0]['_source_trailing_unlabelled_empty_cells'], 2)
        rows = list(csv_rows(io.StringIO('code;value; \n064001;2\n'), ';', 0, trailing_unlabelled_blanks=True))
        self.assertEqual(rows, [{'code': '064001', 'value': '2'}])

    def test_waste_aggregation_omits_fields_without_inventing_zero(self):
        rows = list(csv_rows(io.StringIO('a;b;c;d;e;reference;amount;share\n1;2;3;4;5;Vedi aggregazione: TEST;-\n'),
                             ';', 0, waste_aggregations=True))
        self.assertIsNone(rows[0]['share'])
        self.assertEqual(rows[0]['_source_omitted_fields'], ['share'])

    def test_sparse_jsonstat_does_not_create_observations(self):
        fixture = {'id': ['REF_AREA', 'TIME_PERIOD'], 'size': [2, 2],
                   'dimension': {'REF_AREA': {'category': {'index': {'064002': 1, '064001': 0}, 'label': {}}},
                                 'TIME_PERIOD': {'category': {'index': ['2024', '2025'], 'label': {}}}},
                   'value': {'0': 0, '3': None}, 'status': {'3': 'c'}}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source.json'
            path.write_text(json.dumps(fixture))
            output = Path(directory) / 'fixture.rows.jsonl.gz'
            evidence = profile(path, {'handler': 'jsonstat'}, test_geography(), output)
            self.assertEqual(evidence['numeric_cells'], 1)
            self.assertEqual(evidence['absent_or_null_cells'], 3)
            with gzip.open(output, 'rt') as handle:
                rows = [json.loads(line) for line in handle]
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]['source']['value'], 0)
            self.assertIsNone(rows[1]['source']['value'])
            self.assertEqual(rows[1]['source']['source_status'], 'c')

    def test_jsonstat_out_of_range_index_rejected(self):
        fixture = {'id': ['REF_AREA'], 'size': [1], 'dimension': {'REF_AREA': {'category': {'index': ['064001']}}}, 'value': {'1': 20}}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source.json'; path.write_text(json.dumps(fixture))
            output = Path(directory) / 'fixture.rows.jsonl.gz'
            with self.assertRaisesRegex(ValueError, 'outside dimensions'):
                profile(path, {'handler': 'jsonstat'}, test_geography(), output)
            self.assertFalse(output.exists())

    def test_geojson_count_detects_silent_truncation(self):
        try:
            import shapely  # Optional collection dependencies.
        except ImportError:
            self.skipTest('Optional collection spatial dependencies not installed')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source.json'
            path.write_text(json.dumps({'type': 'FeatureCollection', 'features': []}))
            with self.assertRaisesRegex(ValueError, 'independent source count'):
                profile(path, {'handler': 'geojson', 'expected_count': 1}, test_geography(), Path(directory) / 'fixture.rows.jsonl.gz')


if __name__ == '__main__':
    unittest.main()
