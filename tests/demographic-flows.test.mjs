import assert from 'node:assert/strict';
import {test} from 'node:test';
import {buildDemographicFlows} from '../server/utils/demographicFlows.ts';

const source = {id:'istat_balance',title:'Bilancio demografico annuale',publisher:'ISTAT',url:'https://demo.istat.it/app/?i=P02&l=it',license:'CC BY 4.0',verified_at:'2026-10-16'};
const scopes = [{code:'064033',name:'Fontanarosa'},{code:null,name:'Irpinia'}];
const row = (code,indicator,period,value,status='observed') => ({code,indicator,period,value,status,dataset_id:'istat_balance'});
const natural = (code,period,births,deaths) => [row(code,'births',period,births),row(code,'deaths',period,deaths),row(code,'natural_balance',period,births-deaths)];
const foreign = (code,period,arrivals,departures) => [row(code,'foreign_immigrants',period,arrivals),row(code,'foreign_emigrants',period,departures),row(code,'foreign_migration_balance',period,arrivals-departures)];

test('demographic components retain original non-negative event counts and exact source balance', () => {
  const result = buildDemographicFlows([
    ...natural('064033','2024',17,45),...natural('064033','2025',16,46),
    ...foreign('064033','2024',13,7),...foreign('064033','2025',26,5),
  ],scopes,source,{'2025':'Provisional (p)'});
  const births = result.get('natural_balance');
  assert.equal(births.kind,'natural');
  assert.deepEqual(births.sources,[source]);
  assert.equal(births.period_notes['2025'],'Provisional (p)');
  assert.equal(births.series[0].values[1].positive.value,16);
  assert.equal(births.series[0].values[1].negative.value,46);
  assert.equal(births.series[0].values[1].balance.value,-30);
  assert.equal(result.get('foreign_migration_balance').series[0].values[1].positive.value,26);
  assert.equal(result.get('foreign_migration_balance').series[0].values[1].negative.value,5);
  assert.equal(result.get('foreign_migration_balance').series[0].values[1].balance.value,21);
});

test('provincial flows keep the same paired cohort throughout every source period', () => {
  const rows = [
    ...natural('064033','2024',17,45),...natural('064033','2025',16,46),
    ...natural('064036','2024',20,30),...natural('064036','2025',19,35),
    ...natural('064001','2025',18,32),
  ];
  const result = buildDemographicFlows(rows,scopes,source).get('natural_balance');
  const series = result.series[1];
  assert.match(series.scope,/^2 comuni/);
  assert.deepEqual(series.values.map(point=>point.positive.value),[37,35]);
  assert.deepEqual(series.values.map(point=>point.negative.value),[75,81]);
  assert.deepEqual(series.values.map(point=>point.balance.value),[-38,-46]);
  assert.ok(series.values.every(point=>point.positive.coverage===2 && point.negative.coverage===2 && point.balance.coverage===2));
  for(const point of series.values) assert.equal(point.positive.value-point.negative.value,point.balance.value);
});

test('missing, suppressed and absent components never create zero events or a reconstructed net', () => {
  const rows = [
    ...natural('064033','2024',17,45),row('064033','births','2025',0),
    row('064033','deaths','2025',null,'suppressed'),row('064033','natural_balance','2025',null,'missing'),
    ...natural('064036','2024',20,30),...natural('064036','2025',19,35),
  ];
  const result = buildDemographicFlows(rows,[...scopes,{code:'064001',name:'Aiello del Sabato'}],source).get('natural_balance');
  const point = result.series[0].values.at(-1);
  assert.deepEqual(point.positive,{period:'2025',value:0,status:'observed',coverage:1});
  assert.equal(point.negative.value,null);assert.equal(point.negative.status,'suppressed');
  assert.equal(point.balance.value,null);assert.equal(point.balance.status,'missing');
  assert.equal(result.series[1].values.at(-1).positive.value,19);
  assert.equal(result.series[1].values.at(-1).positive.coverage,1);
  assert.ok(result.series[2].values.every(value=>value.positive.status==='unavailable' && value.positive.value===null));
  const noCohort = buildDemographicFlows(rows,[{code:null,name:'Irpinia'}],source).get('foreign_migration_balance');
  assert.deepEqual(noCohort.series[0].values,[]);
});

test('inconsistent, mixed-source or malformed event counts fail closed', () => {
  const original = natural('064033','2025',16,46);
  assert.throws(()=>buildDemographicFlows([...original.slice(0,2),{...original[2],value:-29}],scopes,source),/reconcile/);
  assert.throws(()=>buildDemographicFlows(original.map(value=>({...value,dataset_id:'other'})),scopes,source),/one original source/);
  assert.throws(()=>buildDemographicFlows([...original,original[0]],scopes,source),/Duplicate/);
  assert.throws(()=>buildDemographicFlows(original.map(value=>({...value,period:'2025-01'})),scopes,source),/annual/);
  assert.throws(()=>buildDemographicFlows([{...original[0],value:-1}],scopes,source),/cannot be negative/);
  assert.throws(()=>buildDemographicFlows([{...original[0],value:1.5}],scopes,source),/Invalid/);
  assert.throws(()=>buildDemographicFlows([{...original[0],value:null}],scopes,source),/Invalid/);
});
