import assert from 'node:assert/strict';
import {test} from 'node:test';
import {percentageCells,metricVisual,historyVariant,historyPresentation,visibleStoryMetrics,storySources} from '../app/utils/metricVisuals.ts';
const point = (period,value,status='observed') => ({period,value,status,coverage:value===null ? 0 : 1});
const source = {id:'latest',title:'Latest source',publisher:'Institution',url:'https://example.org/latest',license:null,verified_at:'2026-10-21'};
const metric = (id='population',code='064033',values=[point('2024',1)]) => ({id,category:'demography',unit:'persons',label:id,description:'Source definition',aggregation:'sum',periods:values.map(point=>point.period),latest_period:values.at(-1)?.period,sources:[source],has_monthly:false,distribution:[],series:[{code,name:code ?? 'Irpinia',current:values.at(-1),history:{scope:code ?? 'Irpinia',label:id,values},monthly:null}]});

test('single-territory snapshots never become peer distributions or invented histories',()=>{
  for (const id of ['population','asia_local_units','asia_employees','municipal_service_spending','admin_historic_spending_per_person','solidarity_fund','utilised_agricultural_area','vineyard_area','olive_area','waste_per_person','annual_temperature','hot_days','frost_days','graduate_residents','soil_consumed_ha']) {
    assert.equal(metricVisual(metric(id)),'counter',id);
    assert.equal(historyPresentation(metric(id)),null,id);
  }
  assert.equal(metricVisual(metric('population',null)),'counter');
  const comparison=metric();comparison.series.push({...comparison.series[0],code:'064036'});
  assert.equal(metricVisual(comparison),'distribution');
});

test('catalogue and investment records use headline counts without statistical charts',()=>{
  for (const category of ['culture','investments']) {
    const snapshot={...metric('snapshot'),category};
    assert.equal(metricVisual(snapshot),'counter');
    assert.equal(metricVisual({...snapshot,series:[...snapshot.series,...snapshot.series]}),'counter');
  }
  assert.equal(metricVisual(metric('pharmacy_location_count')),'counter');
});

test('a separately sourced historical companion does not append the current estimate or census',()=>{
  const latest=metric('population','064033',[point('2026-01-01',2832)]);
  const old=metric('resident_population_history','064033',[point('1951',4900),point('2024',2846)]);
  old.sources=[{...source,id:'historic',url:'https://example.org/historic'}];
  latest.historical={metric:old,series:old.series.map(item=>({code:item.code,name:item.name,history:item.history}))};
  const result=historyPresentation(latest);
  assert.equal(result.separate,true);assert.equal(metricVisual(latest),'history');
  assert.deepEqual(result.series[0].history.values.map(point=>point.period),['1951','2024']);
  assert.equal(latest.series[0].current.period,'2026-01-01');
  assert.deepEqual(visibleStoryMetrics([latest,old]).map(item=>item.id),['population']);
  assert.deepEqual(storySources(latest).map(item=>item.id),['latest','historic']);
  latest.historical.series[0].history.values=[point('1951',null,'unavailable'),point('2024',null,'unavailable')];
  assert.equal(metricVisual(latest),'counter');
  assert.equal(storySources(latest).length,2);
});

test('original demographic pairs receive their own visual while comparisons keep the net indicator',()=>{
  const snapshot=metric('natural_balance','064033',[point('2024',-28),point('2025',-30)]);
  snapshot.demographic_flow={kind:'natural'};
  assert.equal(metricVisual(snapshot),'flows');
  snapshot.series.push({...snapshot.series[0],code:'064036'});
  assert.equal(metricVisual(snapshot),'history');
  assert.equal(historyVariant(snapshot),'line');
});

test('a 100-cell percentage graphic retains fractional values, observed zero and absence',()=>{
  const cells=percentageCells(8.16);
  assert.equal(cells.length,100);assert.ok(Math.abs(cells.reduce((sum,value)=>sum+value,0)-8.16)<1e-10);
  assert.equal(cells.filter(value=>value===1).length,8);
  assert.ok(percentageCells(0).every(value=>value===0));assert.ok(percentageCells(100).every(value=>value===1));
  for(const value of [null,NaN,-1,101])assert.equal(percentageCells(value),null);
});

test('historical geometry follows measured quantities and the source actually drawn',()=>{
  for(const id of ['natural_balance','foreign_migration_balance','soil_net_change_ha'])assert.equal(historyVariant(metric(id)),'bars');
  for(const id of ['resident_population_history','historic_agricultural_holdings','private_households'])assert.equal(historyVariant(metric(id)),'area');
  assert.equal(historyVariant(metric('annual_temperature')),'line');
});
