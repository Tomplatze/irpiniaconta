"""Evidence-backed adapter checks for geography, source ordering and missingness."""
from pathlib import Path
import json
import tempfile
import unittest

from etl.adapters.registry import parse_register
from etl.adapters.istat_demography import parse_population
from etl.adapters.istat_agriculture import parse_export

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'tests' / 'fixtures' / 'istat'


class IstatAdapterTests(unittest.TestCase):
    """Protect source interpretation using the actual retained official snapshots."""

    def setUp(self) -> None:
        """Derive expected geography from the downloaded official register."""
        self.codes = {item['code'] for item in parse_register(RAW / 'istat_registry_2026.xlsx')}

    def test_registry_preserves_six_character_codes_and_montoro(self) -> None:
        """Montoro's noncontiguous suffix must survive canonical reconciliation."""
        self.assertEqual(len(self.codes), 118)
        self.assertIn('064121', self.codes)
        self.assertIn('064033', self.codes)
        self.assertTrue(all(len(code) == 6 for code in self.codes))

    def test_population_published_totals_reconcile(self) -> None:
        """The estimate total is read once, avoiding age-999 double counting."""
        rows = parse_population(RAW / 'istat_demography_2026_avellino.zip')
        population = [row for row in rows if row.indicator_id == 'population']
        self.assertEqual({row.municipality_code for row in population}, self.codes)
        self.assertEqual(sum(row.value for row in population if row.value is not None), 393093)
        self.assertEqual(next(row.value for row in population if row.municipality_code == '064033'), 2832)

    def test_agriculture_decodes_source_category_order(self) -> None:
        """Source ARU/HO order must not be confused with the request's HO/ARU order."""
        rows = parse_export(RAW / 'istat_agriculture_2020_avellino.json', self.codes)
        fontanarosa = {row.indicator_id: row.value for row in rows if row.municipality_code == '064033'}
        self.assertEqual(len(rows), 236)
        self.assertEqual(fontanarosa['agricultural_holdings'], 175)
        self.assertEqual(fontanarosa['utilised_agricultural_area'], 563.23)

    def test_agriculture_preserves_missing_and_confidential_values(self) -> None:
        """Absent cells and confidentiality flags must not become numeric zeros."""
        source = json.loads((RAW / 'istat_agriculture_2020_avellino.json').read_text())
        source['value'].pop('0')
        source['status'] = {'1': 'c'}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source.json'
            path.write_text(json.dumps(source))
            rows = parse_export(path, self.codes)
        self.assertEqual((rows[0].value, rows[0].status), (None, 'missing'))
        self.assertEqual((rows[1].value, rows[1].status), (None, 'suppressed'))

    def test_agriculture_rejects_geographic_drift(self) -> None:
        """A missing expected municipality is a failed integration, not full coverage."""
        with self.assertRaisesRegex(ValueError, 'geography'):
            parse_export(RAW / 'istat_agriculture_2020_avellino.json', self.codes - {'064033'})


if __name__ == '__main__':
    unittest.main()
