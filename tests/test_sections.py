"""Regression checks for source semantics and atomic section publication."""
from copy import deepcopy
from pathlib import Path
import gzip
import hashlib
import json
import tempfile
import unittest
from unittest.mock import patch
from etl import section_normalization as normalize
from etl.sections import validate_cells, validate_publication, publish, publication_lock, ensure_map


def fixture(directory: str, rows: list[dict]) -> dict:
    path=Path(directory)/'rows.jsonl.gz'
    with gzip.open(path,'wt') as handle:
        for row in rows:handle.write(json.dumps(row)+'\n')
    return {'id':'fixture','staging_file':path.name,'staging_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


class MetricSemantics(unittest.TestCase):
    def test_breakdown_with_a_different_unit_requires_an_explicit_parent_unit(self):
        municipalities = [{'code': f'064{i:03}', 'name': str(i)} for i in range(1, 119)]
        parent = {'id': 'farms', 'category': 'agriculture', 'unit': 'holdings', 'cells': [normalize.cell('064001', '2020', 13, 'observed')]}
        breakdown = {'id': 'cattle', 'category': 'agriculture', 'unit': 'heads', 'presentation_role': 'supporting_breakdown',
                     'breakdown_parent': 'farms', 'cells': [normalize.cell('064001', '2020', 10, 'observed')]}
        document = {'municipalities': municipalities, 'categories': [{'id': 'agriculture'}], 'metrics': [parent, breakdown]}
        with self.assertRaisesRegex(ValueError, 'Invalid breakdown parent'):
            validate_publication(document)
        parent['breakdown_unit'] = 'heads'
        validate_publication(document)

    def test_unchanged_map_uses_verified_geometry_without_optional_geographic_libraries(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'data/collection').mkdir(parents=True)
            source = root / 'data/collection/municipal-boundaries.geojson'
            source.write_bytes(b'Synthetic boundary input')
            original = json.dumps({'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest()})
            (root / 'data/sections-map.json').write_text(original)
            with patch('etl.sections.build_map', side_effect=ImportError('Geographic libraries not installed')):
                ensure_map(root)
            self.assertEqual((root / 'data/sections-map.json').read_text(), original)

    def test_changed_boundary_cannot_silently_reuse_a_stale_map(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'data/collection').mkdir(parents=True)
            (root / 'data/collection/municipal-boundaries.geojson').write_bytes(b'Synthetic changed boundary')
            (root / 'data/sections-map.json').write_text('{"source_sha256":"old"}')
            with patch('etl.sections.build_map', side_effect=ImportError('Geographic libraries not installed')), \
                    self.assertRaisesRegex(ValueError, 'requirements-collection.txt'):
                ensure_map(root)
            self.assertEqual((root / 'data/sections-map.json').read_text(), '{"source_sha256":"old"}')

    def test_concurrent_publications_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); (root/'data').mkdir()
            with patch('etl.sections.ROOT',root), publication_lock():
                with self.assertRaisesRegex(RuntimeError,'Another section publication'):
                    with publication_lock():
                        self.fail('The second publisher must not acquire the lock')

    def test_numeric_conventions_preserve_missing_and_zero(self):
        self.assertEqual(normalize.number('1.317,582','italian'),(1317.582,'observed'))
        self.assertEqual(normalize.number('0'),(0.0,'observed'))
        self.assertEqual(normalize.number('#VALUE!'),(None,'missing'))
        with self.assertRaises(ValueError):normalize.number('1,2')
        with self.assertRaises(ValueError):normalize.number(True)

    def test_disclosure_and_anomaly_flags_block_publication(self):
        recipe={'value':'Valore','flags':True,'number_format':'italian'}
        self.assertEqual(normalize.observed_value({'Valore':'100','Privacy':'cod_privacy'},recipe),(None,'suppressed'))
        self.assertEqual(normalize.observed_value({'Valore':'100','Anomalia':'cod_anomalo'},recipe),(None,'missing'))
        self.assertEqual(normalize.observed_value({'Valore':'0','Privacy':'','Anomalia':''},recipe),(0.0,'observed'))

    def test_multi_location_project_has_one_regional_identity(self):
        rows=[{'municipality_codes':['064001','064002'],'source':{'CUP':'A','local':'1'}},
              {'municipality_codes':['064001'],'source':{'CUP':'B','local':'1'}}]
        with tempfile.TemporaryDirectory() as directory:
            source=fixture(directory,rows)
            cells,extras=normalize.distinct(Path(directory),[source],{'keys':['CUP','local'],'period':'2026-06-13'})
        self.assertEqual(extras['regional_distinct']['2026-06-13'],2)
        self.assertEqual(sum(row['value'] for row in cells),3)
        self.assertFalse(any(row['code']=='064003' for row in cells))

    def test_missing_disjoint_category_does_not_become_zero(self):
        rows=[{'municipality_codes':['064001'],'period':'2024','source':{'type':'A','value':2}}]
        recipe={'filters':{'type':['A','B']},'value':'value','combine':True}
        with tempfile.TemporaryDirectory() as directory:
            cells,_=normalize.filtered(Path(directory),[fixture(directory,rows)],recipe)
        self.assertEqual(cells[0]['status'],'missing')
        self.assertIsNone(cells[0]['value'])

    def test_scalar_source_duplicates_are_rejected(self):
        row={'municipality_codes':['064001'],'period':'2024','source':{'value':2}}
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError,'Duplicate'):
                normalize.filtered(Path(directory),[fixture(directory,[row,row])],{'filters':{},'value':'value'})

    def test_foreign_residents_use_and_check_the_source_total_without_double_counting(self):
        rows = [{'municipality_codes':['064001'], 'period':'2026', 'source':{
            'Codice comune':'064001', 'Età':str(age), 'Maschi':'1', 'Femmine':'2'}} for age in range(101)]
        rows.append({'municipality_codes':['064001'], 'period':'2026', 'source':{
            'Codice comune':'064001', 'Età':'999', 'Maschi':'101', 'Femmine':'202'}})
        with tempfile.TemporaryDirectory() as directory:
            cells, _ = normalize.foreign_residents(Path(directory), [fixture(directory,rows)], {})
            self.assertEqual(cells, [normalize.cell('064001','2026-01-01',303,'observed')])
            bad = deepcopy(rows); bad[-1]['source']['Maschi'] = '102'
            with self.assertRaisesRegex(ValueError,'totals do not match'):
                normalize.foreign_residents(Path(directory),[fixture(directory,bad)],{})
            with self.assertRaisesRegex(ValueError,'Incomplete'):
                normalize.foreign_residents(Path(directory),[fixture(directory,rows[:-2]+rows[-1:])],{})
            missing = deepcopy(rows); missing[0]['source']['Maschi'] = ''
            cells, _ = normalize.foreign_residents(Path(directory),[fixture(directory,missing)],{})
            self.assertIsNone(cells[0]['value']); self.assertEqual(cells[0]['status'],'missing')

    def test_grouped_waste_source_cannot_publish_a_municipal_rate(self):
        row={'municipality_codes':['064001'],'period':'2024','source':{'Dato riferito a':'Aggregazione','Totale RU (t)':'100','Totale RD (t)':'80'}}
        with tempfile.TemporaryDirectory() as directory:
            cells,_=normalize.waste(Path(directory),[fixture(directory,[row])],{'measure':'share'})
        self.assertIsNone(cells[0]['value'])
        self.assertEqual(cells[0]['status'],'missing')

    def test_a_missing_weather_day_invalidates_the_annual_statistic(self):
        row={'municipality_codes':['064001'],'source':{'date':'2025-01-01','temperature_2m_mean':4.0,
             'model':'era5_land','grid':{'daily_units':{'temperature_2m_mean':'°C'}}}}
        with tempfile.TemporaryDirectory() as directory:
            cells,extras=normalize.weather(Path(directory),[fixture(directory,[row])],{'measure':'temperature'})
        self.assertIsNone(cells[0]['value']);self.assertTrue(all(row['value'] is None for row in extras['monthly']))

    def test_source_hash_mismatch_fails_before_processing(self):
        with tempfile.TemporaryDirectory() as directory:
            source=fixture(directory,[]);source['staging_sha256']='wrong'
            with self.assertRaisesRegex(ValueError,'checksum'):list(normalize.source_rows(Path(directory),source))

    def test_invalid_publication_is_rejected_before_storage(self):
        registry=[{'code':f'064{i:03}','name':str(i)} for i in range(1,119)]
        document={'municipalities':registry,'categories':[{'id':'test'}],'metrics':[{'id':'test','category':'test',
                   'cells':[normalize.cell('999999','2025',1,'observed')]}],'generated_at':'test','lineage':{}}
        with self.assertRaisesRegex(ValueError,'Unknown'):
            publish(document)

    def test_unknown_codes_and_duplicate_periods_are_rejected(self):
        row=normalize.cell('064001','2024',0,'observed')
        with self.assertRaises(ValueError):validate_cells([row,deepcopy(row)],{'064001'})
        with self.assertRaises(ValueError):validate_cells([row],{'064002'})


if __name__=='__main__':unittest.main()
