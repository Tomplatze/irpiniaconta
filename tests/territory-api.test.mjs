import assert from 'node:assert/strict';
import { test } from 'node:test';
const base=process.env.ATLAS_TEST_URL || 'http://127.0.0.1:3000';
const get=async(path)=>{const response=await fetch(new URL(path,base));assert.equal(response.status,200);return response.json();};

test('agricultural breakdowns retain animal counts, coverage and missing cells without standalone cards',async()=>{
  const town=await get('/api/territory?code=064033');
  const metrics=town.categories.flatMap(category=>category.metrics);
  const metric=id=>metrics.find(item=>item.id===id);
  assert.equal(metric('livestock_farms').series[0].current.value,13);
  assert.equal(metric('livestock_farms').breakdown.find(item=>item.metric.id==='breakdown_livestock_cattle').series[0].current.value,10);
  assert.equal(metric('organic_area').series[0].current.value,105.42);
  assert.equal(metric('organic_farms').series[0].current.value,9);
  assert.deepEqual(metric('private_households').periods,['2020','2021','2022','2023','2024']);
  assert.ok(!metrics.some(item=>['livestock_cattle','landslide_hazard_area','flood_hazard_area'].includes(item.id)));
  const buffalo=metric('livestock_farms').breakdown.find(item=>item.metric.id==='breakdown_livestock_buffalo');
  assert.equal(buffalo.series[0].current.value,null);
  assert.notEqual(buffalo.series[0].current.status,'observed');
  const province=await get('/api/territory');
  const agriculture=province.categories.find(category=>category.id==='agriculture').metrics;
  assert.equal(agriculture.find(item=>item.id==='livestock_farms').series[0].current.coverage,118);
  assert.equal(agriculture.find(item=>item.id==='livestock_farms').breakdown.find(item=>item.metric.id==='breakdown_livestock_cattle').series[0].current.coverage,89);
  assert.equal(agriculture.find(item=>item.id==='organic_area').series[0].current.coverage,114);
});

test('shared territory publication preserves all 46 definitions and provincial aggregation',async()=>{
  const result=await get('/api/territory');
  assert.equal(result.categories.length,10);assert.equal(result.municipalities.length,118);
  const metrics=result.categories.flatMap(category=>category.metrics);
  assert.equal(metrics.length,46);assert.equal(result.scopes[0].code,null);
  for(const metric of metrics){assert.equal(metric.distribution.length,118);assert.equal(metric.series.length,1);assert.ok(!('recipe' in metric));}
  const income=metrics.find(metric=>metric.id==='irpef_income_mean');
  const previous=await get('/api/section?category=economy&metric=irpef_income_mean');
  assert.deepEqual(income.series[0].current,previous.current);assert.deepEqual(income.series[0].history,previous.history);
  assert.equal(income.series[0].current.coverage,118);assert.match(income.series[0].history.scope,/^17 comuni/);
  assert.equal(metrics.find(metric=>metric.id==='pnrr_projects').series[0].current.value,2938);
  const foreign=metrics.find(metric=>metric.id==='foreign_residents');
  assert.equal(foreign.latest_period,'2026-01-01');
  assert.equal(foreign.series[0].current.value,17051);
  assert.equal(foreign.series[0].current.coverage,118);
  assert.equal(foreign.sources[0].id,'istat-foreign-age-2026');
});

test('municipality and overlaid comparisons share exact latest observations and sparse histories',async()=>{
  const one=await get('/api/territory?code=064033');
  const comparison=await get('/api/territory?codes=064033,064036,064008,064005');
  assert.deepEqual(one.categories.map(item=>item.id),comparison.categories.map(item=>item.id));
  for(const category of one.categories){
    const peers=comparison.categories.find(item=>item.id===category.id);
    for(const metric of category.metrics){
      const peerMetric=peers.metrics.find(item=>item.id===metric.id);
      assert.deepEqual(metric.series[0],peerMetric.series[0]);assert.equal(peerMetric.series.length,4);
      const observed=metric.distribution.find(item=>item.code==='064033');
      assert.equal(metric.series[0].current.value,observed.value);assert.equal(metric.series[0].current.period,metric.latest_period);
    }
  }
  const climate=one.categories.flatMap(item=>item.metrics).find(item=>item.id==='annual_temperature');
  const foreign=one.categories.flatMap(item=>item.metrics).find(item=>item.id==='foreign_residents');
  assert.equal(foreign.series[0].current.value,141);
  assert.deepEqual(foreign.periods,['2026-01-01']);
  assert.equal(climate.series[0].monthly.values.length,12);
  assert.ok(climate.series[0].history.values.slice(0,-1).every(point=>point.value===null));
  assert.equal((await get('/api/territory?code=064121')).scopes[0].name,'Montoro');
});

test('unknown, repeated, excessive and conflicting scopes are rejected',async()=>{
  for(const query of ['code=064061','codes=064033','codes=064033,064033','codes=064033,064036,064008,064005,064001','codes=','code=../../x','code=064033&codes=064036','codes=064033&codes=064036']){
    const response=await fetch(new URL(`/api/territory?${query}`,base));assert.ok([400,404].includes(response.status),query);
  }
});

test('demographic component counts reconcile with their original municipal net series',async()=>{
  const result=await get('/api/territory?code=064033');
  const metrics=result.categories.flatMap(item=>item.metrics);
  for(const [id,positive,negative,net] of [['natural_balance',11,41,-30],['foreign_migration_balance',23,2,21]]) {
    const metric=metrics.find(item=>item.id===id);
    const flow=metric.demographic_flow;
    assert.equal(flow.series.length,1);assert.equal(flow.series[0].code,'064033');
    assert.equal(flow.sources[0].publisher,'ISTAT');assert.equal(flow.period_notes['2025'],'Provisional (p)');
    assert.deepEqual(flow.series[0].values.map(point=>point.period),['2021','2022','2023','2024','2025']);
    const latest=flow.series[0].values.at(-1);
    assert.equal(latest.positive.value,positive);assert.equal(latest.negative.value,negative);assert.equal(latest.balance.value,net);
    for(const point of flow.series[0].values) {
      assert.equal(point.positive.value-point.negative.value,point.balance.value);
      assert.equal(point.balance.value,metric.series[0].history.values.find(item=>item.period===point.period).value);
    }
  }
});

test('agricultural and population companion histories preserve distinct source definitions and latest periods',async()=>{
  const result=await get('/api/territory?code=064033');
  const metrics=result.categories.flatMap(item=>item.metrics);
  assert.equal(metrics.length,46);assert.ok(!metrics.some(metric=>metric.id==='historic_vineyard_area'));
  const population=metrics.find(metric=>metric.id==='population');
  assert.equal(population.series[0].current.period,'2026-01-01');
  assert.equal(population.historical.metric.latest_period,'2024');
  assert.ok(!population.historical.series[0].history.values.some(point=>point.period.startsWith('2026')));
  for(const [id,expected] of [['utilised_agricultural_area',[1307.98,1299.99,923.77,627.67]],['vineyard_area',[244.02,94.94,103.45,68.79]],['olive_area',[133.7,131.91,167.23,162.18]]]) {
    const metric=metrics.find(item=>item.id===id);
    assert.equal(metric.series[0].current.period,'2020');assert.equal(metric.historical.metric.latest_period,'2010');
    assert.equal(metric.historical.metric.sources[0].staging_sha256,'3e218f3ea2f7db5c6bd758123f964cd3260c1c75da93d7d173af62e8f2048e9c');
    assert.deepEqual(metric.historical.series[0].history.values.map(point=>point.period),['1982','1990','2000','2010']);
    assert.deepEqual(metric.historical.series[0].history.values.map(point=>point.value),expected);
  }
  assert.ok(!metrics.find(metric=>metric.id==='soil_consumed_ha').historical);
  const montoro=await get('/api/territory?code=064121');
  for(const metric of montoro.categories.flatMap(item=>item.metrics).filter(item=>['utilised_agricultural_area','vineyard_area','olive_area','agricultural_holdings'].includes(item.id))) {
    assert.ok(metric.historical.series[0].history.values.every(point=>point.value===null && point.status==='unavailable'));
  }
});

test('municipal breakdowns use source categories and preserve missing observations', async () => {
  const result=await get('/api/territory?code=064033');
  const metrics=result.categories.flatMap(category=>category.metrics);
  const sectors=metrics.find(metric=>metric.id==='asia_local_units').breakdown;
  const crops=metrics.find(metric=>metric.id==='utilised_agricultural_area').breakdown;
  assert.equal(sectors.length,17);assert.equal(crops.length,24);
  const trade=sectors.find(entry=>entry.metric.id==='breakdown_asia_g');
  assert.equal(trade.series[0].current.value,39);assert.equal(trade.series[0].current.period,'2023');
  const fruit=crops.find(entry=>entry.metric.id==='breakdown_crops_fruit');
  assert.equal(fruit.series[0].current.value,19.04);
  assert.equal(fruit.historical.metric.latest_period,'2010');
  assert.deepEqual(fruit.historical.series[0].history.values.map(point=>point.value),[135.61,63.93,63.38,18.77]);
  const cereals=crops.find(entry=>entry.metric.id==='breakdown_crops_cereals');
  assert.equal(cereals.series[0].current.value,121.04);assert.equal(cereals.series[0].current.period,'2020');
  assert.ok(cereals.metric.sources.some(source=>source.id==='istat-df_dcat_censagric2020_crops_all'));
  assert.ok(crops.some(entry=>entry.series[0].current.status==='unavailable' && entry.series[0].current.value===null));
  assert.ok(!metrics.some(metric=>metric.id.startsWith('breakdown_')));
});
