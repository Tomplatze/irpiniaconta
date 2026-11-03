"""Tests for privacy and internal consistency of aggregate health snapshots."""
import unittest

from etl.health_publication import validate


def sample() -> dict:
    """Create synthetic, non-personal observations for the publication contract."""
    sources = [{'id': key, 'title': key, 'publisher': 'Example', 'url': 'https://example.org', 'period': '2020', 'rights': 'Example'}
               for key in ('a', 'b', 'c', 'd', 'e')]
    series = {code: {territory: [{'year': 2020, 'value': 10.0}] for territory in ('Avellino', 'Campania', 'Italia')}
              for code in ('01SAL001', '01SAL006', '01SAL020', '01SAL007')}
    causes = [{'code': code, 'name': 'Example', 'points': [{'year': year, 'value': 110} for year in range(2018, 2024)]}
              for code in ('2', '4_1', '5', '6', '7', '8_3')]
    sites = {'Maschi': ['Prostata', 'Polmone', 'Colon e retto', 'Vescica, tumori maligni', 'Stomaco'],
             'Femmine': ['Mammella', 'Colon e retto', 'Tiroide', 'Utero, corpo', 'Polmone']}
    cancer = [{'label': label, 'entries': [{'name': name, 'value': 2, 'low': 1, 'high': 3} for name in names]}
              for label, names in sites.items()]
    return {'version': 1, 'sources': sources, 'series': series, 'causes': causes, 'cancer': cancer,
            'autism': {'value': 100, 'source': 'a', 'period': '2020'},
            'survey': {'value': 5, 'low': 4, 'high': 6, 'source': 'b', 'period': '2020'},
            'beds': {'total': 10, 'source': 'c', 'year': 2020,
                     'byType': [{'name': name, 'value': value} for name, value in [('Acuti', 8), ('Riabilitazione', 1), ('Lungodegenza', 1)]],
                     'byRegime': [{'name': name, 'value': value} for name, value in [('Degenza ordinaria', 7), ('Day hospital', 1), ('Day surgery', 1), ('Degenza a pagamento', 1)]],
                     'byProvider': [{'name': name, 'value': value} for name, value in [('Azienda ospedaliera', 6), ('Ospedali a gestione diretta', 2), ('Case di cura private accreditate', 2)]]},
            'admissions': {'total': 1000, 'source': 'd', 'year': 2020},
            'staff': {'total': 10, 'source': 'e', 'year': 2020, 'physicians': 1, 'nurses': 2,
                      'roles': [{'name': name, 'value': 2} for name in ('Sanitario', 'Tecnico', 'Amministrativo', 'Professionale', 'Non classificato')]}}


class HealthPublicationTests(unittest.TestCase):
    def test_valid_aggregate(self):
        validate(sample())

    def test_rejects_small_or_granular_health_data(self):
        small = sample()
        small['causes'][0]['points'][0]['value'] = 3
        with self.assertRaises(ValueError):
            validate(small)
        granular = sample()
        granular['cancer'][0]['entries'][0]['district'] = 'Example'
        with self.assertRaises(ValueError):
            validate(granular)
        geographic = sample()
        geographic['series']['01SAL001']['Comune'] = [{'year': 2020, 'value': 1}]
        with self.assertRaises(ValueError):
            validate(geographic)

    def test_rejects_inconsistent_totals_and_intervals(self):
        broken = sample()
        broken['beds']['byType'][0]['value'] = 9
        with self.assertRaises(ValueError):
            validate(broken)
        broken = sample()
        broken['cancer'][0]['entries'][0]['low'] = 4
        with self.assertRaises(ValueError):
            validate(broken)


if __name__ == '__main__':
    unittest.main()
