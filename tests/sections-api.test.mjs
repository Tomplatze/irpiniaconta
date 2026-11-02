import assert from 'node:assert/strict';
import { test } from 'node:test';
const base=process.env.ATLAS_TEST_URL || 'http://127.0.0.1:3000';
const get=async(path)=>{const response=await fetch(new URL(path,base));assert.equal(response.status,200);return response.json();};

test('all ten sections expose curated measures and valid latest periods',async()=>{
  const overview=await get('/api/sections');
  assert.equal(overview.categories.length,10);assert.equal(overview.metric_count,46);assert.equal(overview.municipalities.length,118);
  for(const category of overview.categories){
    assert.ok(category.metrics.length>=3);
    const result=await get(`/api/section?category=${category.id}`);
    assert.equal(result.metric.id,category.primary);assert.equal(result.distribution.length,118);
    assert.equal(result.current.period,result.metric.latest_period);
    assert.ok(result.metrics.every(metric=>metric.sources.length && !('recipe' in metric)));
  }
});

test('regional income recomputes a weighted mean from the published declarants',async()=>{
  const result=await get('/api/section?category=economy&metric=irpef_income_mean');
  const income=await get('/api/explore?indicator=irpef_income_total&period=2024');
  const declarants=await get('/api/explore?indicator=irpef_income_declarants&period=2024');
  const sum=rows=>rows.filter(row=>row.status==='observed').reduce((total,row)=>total+row.value,0);
  assert.ok(Math.abs(result.current.value-sum(income.values)/sum(declarants.values))<.0001);
  assert.equal(result.metric.unit,'EUR/declarant');
  assert.equal(result.current.coverage,118);
  assert.ok(result.history.scope.startsWith('17 comuni'));
  assert.ok(result.history.values.every(point=>point.coverage===17));
});

test('municipal latest values never silently fall back to earlier years',async()=>{
  const result=await get('/api/section?category=mobility&metric=empty_dwellings&code=064033');
  assert.equal(result.current.scope,'Fontanarosa');assert.equal(result.current.period,'2023');
  assert.equal(result.history.values.length,3);
  const source=await get('/api/collection');
  assert.equal(source.summary.collected_records,1714245);
});

test('project identities are distinct province-wide, not summed across locations',async()=>{
  const result=await get('/api/section?category=investments&metric=pnrr_projects');
  assert.equal(result.current.value,2938);
  assert.ok(result.distribution.reduce((total,row)=>total+(row.value??0),0)>result.current.value);
  assert.equal(result.history.values.length,1);
});

test('temperature history makes its ten-point cohort and monthly coverage explicit',async()=>{
  const result=await get('/api/section?category=climate&metric=annual_temperature');
  assert.equal(result.current.coverage,118);assert.equal(result.current.period,'2025');
  assert.ok(result.history.scope.startsWith('10 punti'));
  assert.equal(result.monthly.values.length,12);assert.ok(result.monthly.values.every(value=>value.coverage===118));
  const town=await get('/api/section?category=climate&metric=annual_temperature&code=064033');
  assert.ok(town.history.values.filter(value=>value.status==='observed').length===1);
  assert.ok(town.history.values.slice(0,-1).every(value=>value.value===null));
});

test('undated culture and missing municipalities do not manufacture dates or zero',async()=>{
  const result=await get('/api/section?category=culture&metric=cultural_places');
  assert.equal(result.current.period,'undated');assert.equal(result.current.value,55);
  assert.ok(result.distribution.some(row=>row.value===null && row.status==='unavailable'));
  const map=await get('/api/section-map');assert.equal(map.features.length,118);
});

test('exports are retired and invalid scope or metric requests are rejected',async()=>{
  const response=await fetch(new URL('/api/section-export?category=mobility&metric=empty_dwellings',base));
  assert.equal(response.status,410);
  assert.equal(response.headers.get('content-disposition'),null);
  for(const path of ['/api/section?category=missing','/api/section?category=climate&metric=pnrr_projects','/api/section?category=climate&code=064061','/api/section?category=climate&code=../../config']){
    const invalid=await fetch(new URL(path,base));assert.ok([400,404].includes(invalid.status));
  }
});
