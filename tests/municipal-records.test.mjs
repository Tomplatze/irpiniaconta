import assert from 'node:assert/strict';
import { test } from 'node:test';

const base = process.env.ATLAS_TEST_URL || 'http://127.0.0.1:3000';
async function get(path) { const response = await fetch(new URL(path,base)); return {status:response.status,body:await response.json()}; }
const groups = [['schools','state_school_sites'],['pharmacies','pharmacy_location_count'],['pnrr','pnrr_projects'],['cohesion','cohesion_projects'],['fortified','fortified_sites'],['historic','historic_centres'],['cultural','cultural_places'],['libraries','province_libraries_listed_records']];

test('municipal record lists use the same source identities as the related indicators',async()=>{
  for (const code of ['064104','064008','064033']) {
    const territory = await get(`/api/territory?code=${code}`);
    assert.equal(territory.status,200);
    const metrics=territory.body.categories.flatMap(category=>category.metrics);
    for (const [group,id] of groups) {
      const result=await get(`/api/municipal-records?code=${code}&group=${group}`);
      assert.equal(result.status,200,`${code}/${group}`);
      const metric=metrics.find(item=>item.id===id).series[0].current;
      if (metric.status==='observed') assert.equal(result.body.total,metric.value,`${code}/${group}`);
      for (const record of result.body.records) assert.ok(record.title && record.sourceTitle);
    }
  }
});

test('pagination, source-backed fields and municipality boundaries are preserved',async()=>{
  const schools=(await get('/api/municipal-records?code=064104&group=schools')).body;
  assert.equal(schools.total,4);
  assert.ok(schools.records.some(record=>record.fields.some(field=>field.value==='PIAZZA MICHELE AUFIERO')));
  const pharmacies=(await get('/api/municipal-records?code=064104&group=pharmacies')).body;
  assert.equal(pharmacies.total,1);
  assert.ok(pharmacies.records[0].fields.some(field=>field.value==='Via A. FORGIONE, 2'));
  const first=(await get('/api/municipal-records?code=064104&group=pnrr&limit=8')).body;
  const second=(await get('/api/municipal-records?code=064104&group=pnrr&limit=8&offset=8')).body;
  assert.equal(first.total,14); assert.equal(second.records.length,6);
  assert.ok(second.records.every(record=>!first.records.some(previous=>previous.id===record.id)));
  const other=(await get('/api/municipal-records?code=064033&group=pharmacies')).body;
  assert.ok(other.records.every(record=>record.id!==pharmacies.records[0].id));
  assert.equal((await get('/api/municipal-records?code=064999&group=schools')).status,404);
  assert.equal((await get('/api/municipal-records?code=064104&group=toString')).status,404);
  assert.equal((await get('/api/municipal-records?code=064104&group=schools&limit=31')).status,400);
});

test('municipal school card replaces its chart and generic record dump',async()=>{
  const response=await fetch(new URL('/comuni/064104',base));
  const html=await response.text();
  assert.equal(response.status,200);
  const card=html.match(/<article id="state_school_sites"[\s\S]*?<\/article>/)?.[0];
  assert.ok(card); assert.match(card,/Elenco delle sedi scolastiche/); assert.doesNotMatch(card,/overlay-chart/);
  assert.doesNotMatch(html,/Consulta i luoghi e i record di Sturno/);
  assert.match(html,/Elenco delle farmacie/); assert.match(html,/Elenco dei progetti PNRR/);
});

test('title indexes are complete and individual details retain municipality boundaries',async()=>{
  for (const [code,group,expected] of [['064033','pnrr',33],['064033','cohesion',198],['064008','cohesion',1686],['064104','schools',4],['064104','pharmacies',1]]) {
    const index=await get(`/api/municipal-records?code=${code}&group=${group}&view=index`);
    assert.equal(index.status,200);
    assert.equal(index.body.total,expected);
    assert.equal(index.body.records.length,expected);
    assert.equal(new Set(index.body.records.map(record=>record.id)).size,expected);
    assert.ok(index.body.records.every(record=>record.title && !Object.hasOwn(record,'fields')));
    const id=index.body.records.at(-1).id;
    const detail=await get(`/api/municipal-records?code=${code}&group=${group}&id=${encodeURIComponent(id)}`);
    assert.equal(detail.status,200);
    assert.equal(detail.body.id,id);
    assert.ok(Array.isArray(detail.body.fields));
  }
  const fontanarosa=(await get('/api/municipal-records?code=064033&group=pharmacies&view=index')).body.records[0];
  assert.equal((await get(`/api/municipal-records?code=064104&group=pharmacies&id=${encodeURIComponent(fontanarosa.id)}`)).status,404);
  assert.equal((await get('/api/municipal-records?code=064033&group=pnrr&view=index&id=test')).status,400);
  assert.equal((await get('/api/municipal-records?code=064033&group=pnrr&view=other')).status,400);
});
