"""Weather API validation must reject plausible HTTP-200 responses with missing climate values."""
import json
from pathlib import Path
import unittest
from etl.weather_probe import validate
from etl.geography_probe import dbf_records

ROOT=Path(__file__).resolve().parent.parent


class WeatherTests(unittest.TestCase):
    def test_real_land_model_null_rainfall_is_rejected(self):
        path=ROOT/'data/raw/open_meteo_archive_probe.json'
        if not path.exists():self.skipTest('Raw API sample not bundled')
        with self.assertRaises(ValueError):validate('open_meteo_archive',json.loads(path.read_text()))

    def test_real_verified_models_have_complete_sample_days_and_units(self):
        for provider,filename in [('open_meteo_archive','open_meteo_era5_probe.json'),('nasa_power','nasa_power_probe.json')]:
            path=ROOT/'data/raw'/filename
            if not path.exists():self.skipTest('Raw API sample not bundled')
            self.assertEqual(validate(provider,json.loads(path.read_text()))['validated_days'],7)

    def test_source_boundary_attributes_cover_exact_current_codes(self):
        from etl.pipeline import replay_snapshot
        import csv
        path=ROOT/'data/boundary-attributes-2026.csv'
        if not path.exists():self.skipTest('Collected boundary attributes not available')
        with path.open() as stream:rows=list(csv.DictReader(stream))
        municipalities,_,_=replay_snapshot(ROOT/'data/snapshot.json')
        self.assertEqual(len(rows),118);self.assertEqual({row['PRO_COM_T'] for row in rows},{row['code'] for row in municipalities})
