"""Source-shape regressions for internal historical agriculture companions."""
from copy import deepcopy
from pathlib import Path
import gzip
import hashlib
import json
import tempfile
import unittest

from etl import section_normalization as normalize
from etl.sections import is_public_metric, validate_publication, write_report

ROOT = Path(__file__).resolve().parent.parent


def staged_fixture(directory: str, rows: list[dict]) -> dict:
    """Build a small hash-verified original-row fixture, never a production publication."""
    path = Path(directory) / 'historical-rows.jsonl.gz'
    with gzip.open(path, 'wt') as handle:
        for row in rows:
            handle.write(json.dumps(row) + '\n')
    return {'id': 'fixture', 'staging_file': path.name, 'staging_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


class HistoricalAgriculture(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / 'config/sections.json').read_text())
        self.metrics = {metric['id']: metric for metric in self.config['metrics']}
        self.identities = ['historic_utilised_agricultural_area', 'historic_vineyard_area', 'historic_olive_area', 'historic_fruit_area']

    def row(self, identity: str, value=627.67, flag='') -> dict:
        source = {**self.metrics[identity]['recipe']['filters'], 'Value': value, 'Flags': flag, 'TIME': '2010'}
        return {'municipality_codes': ['064033'], 'period': '2010', 'source': source}

    def test_public_count_and_companion_links_remain_explicit(self):
        self.assertEqual(sum(is_public_metric(metric) for metric in self.metrics.values()), 46)
        self.assertEqual({metric['id'] for metric in self.metrics.values() if metric.get('presentation_role') == 'supporting_history'}, set(self.identities))
        expected = {'population': 'resident_population_history', 'agricultural_holdings': 'historic_agricultural_holdings',
                    'utilised_agricultural_area': self.identities[0], 'vineyard_area': self.identities[1], 'olive_area': self.identities[2]}
        for identity, companion in expected.items():
            recipe = self.metrics[identity]['recipe']
            self.assertEqual(recipe['related_history'], companion)
            self.assertTrue(recipe['show_companion_history'])
        self.assertEqual(self.metrics['breakdown_crops_fruit']['recipe']['related_history'], 'historic_fruit_area')
        self.assertTrue(self.metrics['breakdown_crops_fruit']['recipe']['show_companion_history'])
        self.assertFalse(self.metrics['soil_consumed_ha']['recipe'].get('show_companion_history', False))

    def test_area_crop_dimensions_select_source_measures_without_double_counting(self):
        samples = [self.row(self.identities[0], 627.67), self.row(self.identities[1], 68.79), self.row(self.identities[2], 162.18), self.row(self.identities[3], 18.77)]
        unselected = deepcopy(samples[0]); unselected['source']['ZONA_ALTIM'] = 'MOUNTAIN'; unselected['source']['Value'] = 10000
        with tempfile.TemporaryDirectory() as directory:
            dataset = staged_fixture(directory, [*samples, unselected])
            for identity, expected, data_type, detail, crop in [
                (self.identities[0], 627.67, 'ARU', 'ALL', 'AREATOT'),
                (self.identities[1], 68.79, 'AR', 'WC', 'VINEY'),
                (self.identities[2], 162.18, 'AR', 'WC', 'OLIV'),
                (self.identities[3], 18.77, 'AR', 'WC', 'FRUIT'),
            ]:
                metric = self.metrics[identity]; recipe = metric['recipe']
                self.assertEqual(recipe['sources'], ['istat-historical-agriculture-1982-2010'])
                self.assertEqual((recipe['filters']['TIPO_DATO5'], recipe['filters']['TIPO_DATO5_DETT'], recipe['filters']['UTILTERR_A']), (data_type, detail, crop))
                self.assertEqual(metric['unit'], 'ha')
                cells, _ = normalize.filtered(Path(directory), [dataset], recipe)
                self.assertEqual(cells, [normalize.cell('064033', '2010', expected, 'observed')])

    def test_companions_preserve_source_flags_missing_and_observed_zero(self):
        for identity in self.identities:
            recipe = self.metrics[identity]['recipe']
            for raw, flag, expected, state in [(None, '', None, 'missing'), (0, '', 0, 'observed'), (12, 'c', None, 'suppressed'), (12, 'g', None, 'missing')]:
                with self.subTest(identity=identity, flag=flag, raw=raw), tempfile.TemporaryDirectory() as directory:
                    cells, _ = normalize.filtered(Path(directory), [staged_fixture(directory, [self.row(identity, raw, flag)])], recipe)
                    self.assertEqual((cells[0]['value'], cells[0]['status']), (expected, state))
            with tempfile.TemporaryDirectory() as directory:
                with self.assertRaisesRegex(ValueError, 'Unreviewed source status'):
                    normalize.filtered(Path(directory), [staged_fixture(directory, [self.row(identity, 12, 'unexpected')])], recipe)

    def test_companions_reject_duplicate_or_ambiguous_scalar_cells(self):
        for identity in self.identities:
            row = self.row(identity)
            with self.subTest(identity=identity), tempfile.TemporaryDirectory() as directory:
                with self.assertRaisesRegex(ValueError, 'Duplicate'):
                    normalize.filtered(Path(directory), [staged_fixture(directory, [row, row])], self.metrics[identity]['recipe'])
            row['municipality_codes'].append('064036')
            with tempfile.TemporaryDirectory() as directory:
                with self.assertRaisesRegex(ValueError, 'exactly one municipal association'):
                    normalize.filtered(Path(directory), [staged_fixture(directory, [row])], self.metrics[identity]['recipe'])

    def test_publication_rejects_unknown_roles_and_missing_companions(self):
        registry = [{'code': f'064{index:03}', 'name': str(index)} for index in range(1, 119)]
        document = {'municipalities': registry, 'metrics': [{'id': 'metric', 'category': 'agriculture', 'cells': [],
                     'presentation_role': 'unreviewed'}]}
        with self.assertRaisesRegex(ValueError, 'Unknown presentation role'):
            validate_publication(document)
        del document['metrics'][0]['presentation_role']
        document['metrics'][0]['recipe'] = {'show_companion_history': True, 'related_history': 'not-published'}
        with self.assertRaisesRegex(ValueError, 'Unknown historical companion'):
            validate_publication(document)

    def test_report_distinguishes_public_cards_from_internal_support(self):
        metrics = []
        for identity in ['agricultural_holdings', *self.identities]:
            metric = deepcopy(self.metrics[identity])
            metric.update({'periods': ['1982', '1990', '2000', '2010'], 'latest_period': '2010', 'cells': [], 'sources': []})
            metrics.append(metric)
        document = {'generated_at': 'test', 'metrics': metrics, 'categories': [{'id': 'agriculture'}]}
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / 'docs').mkdir()
            write_report(document, Path(directory))
            report = (Path(directory) / 'docs/SECTIONS.md').read_text()
        self.assertIn('1 selected public metrics', report)
        self.assertIn('4 supporting series', report)
        self.assertIn('## Supporting historical measurements', report)
        selected, supporting = report.split('## Supporting historical measurements')
        self.assertNotIn('`historic_vineyard_area`', selected)
        self.assertIn('`historic_vineyard_area`', supporting)


if __name__ == '__main__':
    unittest.main()
