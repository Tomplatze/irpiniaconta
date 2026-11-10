"""Regression checks for decimal extraction and the provincial totals boundary."""
from decimal import Decimal
import unittest

from etl.energy_publication import check_total, read_row


class EnergyPublicationTests(unittest.TestCase):
    def test_generation_preserves_dash_and_published_total(self):
        values = read_row('Avellino 15,3 - 158,8 1.595,3 4,9 1.774,4', 'Avellino', 6)
        names = ('hydro', 'geothermal', 'solar', 'wind', 'bioenergy', 'total')
        result = check_total(dict(zip(names, values, strict=True)), allow_dash=True)
        self.assertIsNone(result['geothermal'])
        self.assertEqual(result['wind'], 1595.3)
        self.assertEqual(result['total'], 1774.4)

    def test_provincial_total_excludes_separate_regional_total(self):
        text = 'TOTALE 1.434,9 734,5 3.216,5 7.468,3 3.584,9 16.439,1\nTOTALE 16.804,6'
        self.assertEqual(read_row(text, 'TOTALE', 6)[0], Decimal('1434.9'))

    def test_duplicate_rows_missing_consumption_and_inconsistent_totals_fail(self):
        with self.assertRaises(ValueError):
            read_row('Avellino 1,0\nAvellino 2,0', 'Avellino', 1)
        with self.assertRaises(ValueError):
            check_total({'domestic': None, 'total': Decimal('1.0')}, allow_dash=False)
        with self.assertRaises(ValueError):
            check_total({'wind': Decimal('1.0'), 'total': Decimal('10.0')}, allow_dash=True)
