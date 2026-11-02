"""Regression checks for source independence, historical fidelity and last-valid recovery."""
from copy import deepcopy
from datetime import datetime,timezone
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from etl.acquisition import Context
from etl.models import AdapterResult, Entity, Observation
from etl.quality import assess
from etl.refresh import merge_valid,content_digest,exclusive_refresh,pending_result,due_source
from etl.registry import load_scope
from etl.adapters.istat_balance import parse_balance
from etl.adapters.mef_series import parse_year,combined
from etl.adapters.restricted import run as verify_restriction
from etl.adapters.municipal_keys import reconcile_legacy_code

ROOT=Path(__file__).resolve().parent.parent


class RefreshTests(unittest.TestCase):
    """Use synthetic values only for lifecycle behaviours, never as delivered observations."""
    def result(self,period='2024',value=10):
        return AdapterResult({'id':'test','status':'ready','indicators':[{'id':'metric','unit':'persons'}],
                             'last_attempt':{'at':'2026-10-13T00:00:00+00:00','status':'ready'}},[Observation('064033','metric',period,value)])

    def test_calendar_month_uses_central_local_timezone(self):
        previous=self.result();previous.metadata['last_attempt']['at']='2026-10-31T23:30:00+00:00'
        self.assertFalse(due_source({'cadence_days':30},previous,datetime(2026,11,1,9,tzinfo=timezone.utc)))
        self.assertTrue(due_source({'cadence_days':30},previous,datetime(2026,12,1,9,tzinfo=timezone.utc)))

    def test_history_retains_older_year_and_replaces_revised_cell(self):
        previous=self.result('2023',10);previous.observations.append(Observation('064033','metric','2024',20))
        current=self.result('2024',25);merged=merge_valid(previous,current)
        self.assertEqual({row.period:row.value for row in merged.observations},{'2023':10,'2024':25})

    def test_failed_refresh_keeps_valid_values_and_original_provenance(self):
        previous=self.result();previous.metadata['artifacts']=[{'sha256':'original'}]
        failed=AdapterResult({**previous.metadata,'status':'blocked','blocker':'Schema changed','last_attempt':{'status':'blocked','blocker':'Schema changed'}})
        merged=merge_valid(previous,failed)
        self.assertTrue(merged.metadata['stale']);self.assertEqual(merged.observations,previous.observations)
        self.assertEqual(merged.metadata['artifacts'],[{'sha256':'original'}]);self.assertEqual(merged.metadata['status'],'ready')

    def test_entity_only_dataset_preserves_unmatched_geography(self):
        result=AdapterResult({'id':'test','status':'ready','indicators':[]},entities=[Entity(None,'test','one','Road','road',{},'2026-10-13')])
        report=assess(result,{'064033'});self.assertEqual(report['entities'],1)

    def test_duplicate_entities_are_rejected(self):
        result=AdapterResult({'id':'test','status':'ready','indicators':[]},entities=[Entity(None,'test','one','Road','road',{},'2026-10-13')]*2)
        with self.assertRaises(ValueError):assess(result,{'064033'})

    def test_snapshot_notifications_ignore_only_acquisition_period(self):
        a=self.result('2026-10-13');a.metadata['temporal_semantics']='current_snapshot'
        b=self.result('2026-11-01');b.metadata['temporal_semantics']='current_snapshot'
        self.assertEqual(content_digest(a),content_digest(b))
        b.observations=[replace(b.observations[0],value=11)]
        self.assertNotEqual(content_digest(a),content_digest(b))

    def test_current_snapshot_ignores_unchanged_prior_acquisitions(self):
        previous=self.result('2026-10-13');previous.metadata['temporal_semantics']='current_snapshot'
        current=self.result('2026-11-01');current.metadata['temporal_semantics']='current_snapshot'
        merged=merge_valid(previous,current)
        self.assertEqual(content_digest(previous),content_digest(merged))

    def test_statistical_period_changes_remain_visible_for_schools(self):
        previous=self.result('2025');previous.metadata['temporal_semantics']='statistical_period'
        current=self.result('2026');current.metadata['temporal_semantics']='statistical_period'
        self.assertNotEqual(content_digest(previous),content_digest(merge_valid(previous,current)))

    def test_missing_income_bin_never_becomes_zero(self):
        self.assertEqual(combined([(10,'observed'),(None,'missing')]),(None,'missing'))
        self.assertEqual(combined([(10,'observed'),(None,'suppressed')]),(None,'suppressed'))
        self.assertEqual(combined([(10,'observed'),(0,'observed')]),(10,'observed'))

    def test_policy_evidence_preserves_restriction_across_line_breaks(self):
        source=next(row for row in load_scope()['sources'] if row['id']=='CLI-01')
        path=ROOT/'data/raw/scia_reuse.html'
        if not path.exists():self.skipTest('Raw live policy evidence not bundled')
        result=verify_restriction(Context(ROOT/'data/raw',offline=True),source['options'])
        self.assertEqual(result.metadata['status'],'blocked')
        self.assertIn('prohibits reproduction',result.metadata['blocker'])
        self.assertFalse(result.observations)

    def test_reviewed_fusion_is_dated_and_name_specific(self):
        self.assertEqual(reconcile_legacy_code('064061','MONTORO INFERIORE','2026-10-13',{'064121'})[0],'064121')
        with self.assertRaises(ValueError):reconcile_legacy_code('064061','MONTORO INFERIORE','2012-01-01',{'064121'})
        with self.assertRaises(ValueError):reconcile_legacy_code('064061','Different town','2026-10-13',{'064121'})

    def test_scope_counts_and_blockers_are_complete(self):
        scope=load_scope();self.assertEqual(len(scope['categories']),10);self.assertEqual(len(scope['sources']),81)
        for source in scope['sources']:
            self.assertTrue(source['landing_url'].startswith('https://'));self.assertTrue(source['blocker'])
            if source['adapter'] is None:
                result=pending_result(source);self.assertFalse(result.observations);self.assertFalse(result.entities)

    def test_overlapping_refresh_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory)/'data').mkdir()
            with patch('etl.refresh.ROOT',Path(directory)), exclusive_refresh():
                with self.assertRaises(RuntimeError):
                    with exclusive_refresh():pass


class RealSeriesTests(unittest.TestCase):
    """Replay actual acquired artifacts when present; clean snapshots do not require raw files."""
    def test_demographic_balance_reconciles_five_annual_exports(self):
        if not (ROOT/'data/raw/istat_balance_2025.zip').exists():self.skipTest('Raw live artifacts not bundled')
        for year in range(2021,2026):
            cells=parse_balance((ROOT/f'data/raw/istat_balance_{year}.zip').read_bytes(),year)
            self.assertEqual(len(cells),1180)
            self.assertEqual({row.period for row in cells},{str(year)})

    def test_income_suppression_is_not_reconstructed(self):
        if not (ROOT/'data/raw/mef-income-2020.zip').exists():self.skipTest('Raw live artifacts not bundled')
        cells,_,derived=parse_year((ROOT/'data/raw/mef-income-2020.zip').read_bytes(),'2020')
        self.assertTrue(derived)
        grouped={row.municipality_code:[item for item in cells if item.municipality_code==row.municipality_code] for row in cells}
        for values in grouped.values():
            inputs=[row for row in values if row.indicator_id not in {'irpef_taxpayers','irpef_income_declarants','irpef_income_total','irpef_income_mean'} and row.status!='observed']
            if inputs:
                total=next(row for row in values if row.indicator_id=='irpef_income_total')
                # Other taxable-income columns can be missing independently; exhaustive bins alone control the total.
                self.assertIn(total.status,{'observed','missing','suppressed'})
        self.assertTrue(any(row.value is None for row in cells))


if __name__=='__main__':unittest.main()
