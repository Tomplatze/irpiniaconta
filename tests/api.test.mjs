import assert from 'node:assert/strict';
import { test } from 'node:test';

const base = process.env.ATLAS_TEST_URL || 'http://127.0.0.1:3000';

/** Fetch a read-only API response from a running production or development server. */
async function request(path) {
  const response = await fetch(new URL(path, base));
  return { status: response.status, body: await response.json() };
}

test('health verifies the real PostgreSQL publication', async () => {
  const result = await request('/api/health');
  assert.equal(result.status, 200);
  assert.equal(result.body.integrity, 'ok');
  assert.equal(result.body.municipalities, 118);
});

test('catalog exposes all scope sources, licenses and measured coverage', async () => {
  const result = await request('/api/overview');
  assert.equal(result.status, 200);
  assert.equal(result.body.municipalities.length, 118);
  assert.equal(result.body.datasets.length, 81);
  assert.ok(result.body.summary.acquired_at);
  assert.ok(Date.parse(result.body.summary.acquired_at) <= Date.parse(result.body.summary.last_run));
  for (const dataset of result.body.datasets) {
    assert.ok(dataset.publisher && dataset.landing_url && dataset.verified_at);
    for (const indicator of dataset.indicators) {
      assert.equal(indicator.observed_count + indicator.suppressed_count + indicator.missing_count + indicator.absent_count, 118);
    }
  }
});

test('comparison preserves period, real zero and unavailable state', async () => {
  const result = await request('/api/comparison?codes=064033,064036');
  assert.equal(result.status, 200);
  assert.deepEqual(result.body.municipalities.map((row) => row.name), ['Fontanarosa', 'Gesualdo']);
  for (const row of result.body.rows) {
    assert.equal(row.measurements.length, 2);
    for (const measurement of row.measurements) {
      if (measurement.status === 'observed') assert.equal(typeof measurement.value, 'number');
      else assert.equal(measurement.value, null);
    }
  }
  assert.ok(result.body.rows.some((row) => row.measurements.every((measurement) => measurement.status === 'unavailable')));
});

test('explicit indicator/period cannot silently fall back to another year', async () => {
  const overview = (await request('/api/overview')).body;
  const indicator = overview.datasets.flatMap((dataset) => dataset.indicators).find((item) => item.latest_period);
  const result = await request(`/api/comparison?codes=064033,064036&indicator=${indicator.id}&period=${indicator.latest_period}`);
  assert.equal(result.status, 200);
  assert.equal(result.body.rows.length, 1);
  assert.equal(result.body.rows[0].period, indicator.latest_period);
  assert.equal((await request(`/api/comparison?codes=064033,064036&indicator=${indicator.id}&period=1900`)).status, 404);
});

test('invalid, duplicate, unknown and excessive municipal selections are rejected', async () => {
  const cases = [
    ['/api/comparison', 400], ['/api/comparison?codes=064033', 400],
    ['/api/comparison?codes=064033,064033', 400], ['/api/comparison?codes=064033,064999', 404],
    ['/api/comparison?codes=064033,048017', 400], ['/api/comparison?codes=064033,064036&indicator=unknown', 404],
    ['/api/comparison?codes=064033,064036&period=2024', 400],
    ['/api/comparison?codes=064033,064036,064001,064002,064003', 400],
    ['/api/comparison?codes=064033%27,064036', 400],
  ];
  for (const [path, status] of cases) assert.equal((await request(path)).status, status, path);
});

test('four municipalities retain requested order', async () => {
  const result = await request('/api/comparison?codes=064033,064036,064001,064002');
  assert.equal(result.status, 200);
  assert.deepEqual(result.body.municipalities.map((row) => row.code), ['064033', '064036', '064001', '064002']);
});


test('ten sections preserve the agreed catalogue counts', async () => {
  const { body } = await request('/api/catalogue');
  assert.equal(body.sources.length,81);
  assert.deepEqual(body.categories.map((category) => category.expected_items),[9,9,9,7,8,10,4,9,8,8]);
  assert.ok(body.sources.some((source) => source.status === 'restricted'));
  const climate=body.sources.find((source) => source.id === 'CLI-01');
  assert.equal(climate.dataset.status,'blocked');
});

test('historical series keep their original years and reject unknown codes', async () => {
  const { body,status }=await request('/api/series?indicator=births&codes=064033');
  assert.equal(status,200);
  assert.deepEqual(body.municipalities[0].values.map((value) => value.period),['2021','2022','2023','2024','2025']);
  assert.equal((await request('/api/series?indicator=births&codes=064999')).status,404);
  assert.equal((await request('/api/series?indicator=births&codes=064033,064033')).status,400);
});

test('exploration uses one period while public exports are retired', async () => {
  const { body,status }=await request('/api/explore?indicator=irpef_income_mean&period=2020');
  assert.equal(status,200);assert.equal(body.values.length,118);assert.equal(body.period,'2020');
  assert.ok(body.values.some((value) => value.value===null));
  assert.equal((await request('/api/explore?indicator=irpef_income_mean&period=1900')).status,404);
  const csv=await fetch(new URL('/api/export?indicator=births&period=2024',base));
  assert.equal(csv.status,410);
  assert.equal(csv.headers.get('content-disposition'),null);
});

test('entity pagination is bounded and associations remain explicit', async () => {
  const {body,status}=await request('/api/entities?category=culture&limit=2');
  assert.equal(status,200);assert.equal(body.records.length,2);assert.ok(body.total>100);
  const roads=(await request('/api/entities?category=mobility&limit=1')).body;
  assert.equal(roads.records[0].municipality_code,null);
  assert.equal((await request('/api/entities?limit=101')).status,400);
  assert.equal((await request('/api/entities?category=unknown')).status,404);
  assert.equal((await request('/api/entities?code=064999')).status,404);
});

test('catalog separates unfinished integrations from failures and clean ready metadata', async () => {
  const {body}=await request('/api/catalogue');
  assert.ok(body.sources.some((source) => source.status==='pending' && source.adapter===null));
  assert.ok(body.sources.some((source) => source.status==='blocked' && source.adapter));
  for (const source of body.sources.filter((source) => source.status==='ready')) {
    assert.equal(source.blocker,null);
    assert.ok(source.dataset.artifacts.length>0);
  }
});

test('public atlas selects a few indicators while the technical catalogue keeps all fields', async () => {
  const publicView=(await request('/api/atlas')).body;
  const technical=(await request('/api/overview')).body;
  const publicMetrics=publicView.datasets.flatMap(dataset=>dataset.indicators);
  assert.ok(publicMetrics.length<20);
  assert.ok(publicMetrics.length<technical.datasets.flatMap(dataset=>dataset.indicators).length);
  assert.ok(publicMetrics.some(metric=>metric.id==='irpef_income_mean'));
  assert.equal(publicView.municipalities.length,118);
});
