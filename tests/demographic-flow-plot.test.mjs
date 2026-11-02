import assert from 'node:assert/strict';
import {test} from 'node:test';
import {buildDemographicFlowPlot,demographicFlowPeriodNote,observedFlowCount} from '../app/utils/demographicFlowPlot.ts';
const cell = (period,value,status=value===null ? 'unavailable' : 'observed') => ({period,value,status,coverage:status==='observed' ? 1 : 0});
const point = (period,positive,negative,positiveStatus,negativeStatus) => ({period,positive:cell(period,positive,positiveStatus),negative:cell(period,negative,negativeStatus),balance:cell(period,positive===null || negative===null ? null : positive-negative)});
const flow = (kind,values) => ({kind,unit:'persons',positive:{id:'positive',label:'Positive'},negative:{id:'negative',label:'Negative'},sources:[],period_notes:{},series:[{code:'064033',name:'Fontanarosa',scope:'Fontanarosa',values}]});

test('births and deaths use equal absolute scales with non-negative source counts on opposite sides of zero', () => {
  const chart=buildDemographicFlowPlot(flow('natural',[point('2024',10,20),point('2025',20,10)]),420);
  const [births,deaths]=chart.components;
  assert.equal(chart.zeroY,(chart.top+chart.bottom)/2);
  assert.ok(births.points.every(row=>row.y<chart.zeroY && row.value>0));
  assert.ok(deaths.points.every(row=>row.y>chart.zeroY && row.value>0));
  assert.equal(chart.zeroY-births.points[0].y,deaths.points[1].y-chart.zeroY);
  assert.equal(chart.zeroY-births.points[1].y,deaths.points[0].y-chart.zeroY);
  assert.ok(chart.ticks.every(tick=>tick.value>=0 && Number.isInteger(tick.value)));
  assert.equal(chart.hasData,true);
});

test('natural columns stay within their plot and retain actual calendar distances on narrow and wide screens', () => {
  const source=flow('natural',[point('2016',1,3),point('2017',2,4),point('2024',3,5)]);
  const ratio=(Date.parse('2017-01-01')-Date.parse('2016-01-01'))/(Date.parse('2024-01-01')-Date.parse('2016-01-01'));
  for(const width of [240,292,420,720]) {
    const chart=buildDemographicFlowPlot(source,width);
    const periods=chart.periods;
    assert.ok(Math.abs((periods[1].x-periods[0].x)/(periods[2].x-periods[0].x)-ratio)<1e-12);
    assert.ok(chart.components.flatMap(component=>component.points).every(row=>row.x-chart.barWidth/2>=chart.left+4 && row.x+chart.barWidth/2<=chart.right-4));
  }
});

test('foreign arrivals and departures remain two positive series on a single zero-based scale', () => {
  const chart=buildDemographicFlowPlot(flow('foreign',[point('2024',10,20),point('2025',20,10)]),292);
  const [arrivals,departures]=chart.components;
  assert.equal(chart.zeroY,chart.bottom);
  assert.equal(arrivals.points[0].y,departures.points[1].y);
  assert.equal(arrivals.points[1].y,departures.points[0].y);
  assert.ok([...arrivals.points,...departures.points].every(row=>row.y>=chart.top && row.y<=chart.bottom));
  assert.equal(chart.ticks.at(-1).value,0);
});

test('a missing or suppressed component breaks only its own line without becoming zero', () => {
  const chart=buildDemographicFlowPlot(flow('foreign',[point('2021',5,2),point('2022',null,0,'suppressed'),point('2023',6,3)]),420);
  const [arrivals,departures]=chart.components;
  assert.equal(arrivals.points.length,2);assert.equal((arrivals.path.match(/M/g)||[]).length,2);
  assert.equal(departures.points.length,3);assert.equal((departures.path.match(/M/g)||[]).length,1);
  assert.equal(arrivals.areaPaths.length,0);
  assert.equal(departures.areaPaths.length,1);
  assert.match(departures.areaPaths[0],/244\.00.*244\.00 Z$/);
  assert.equal(departures.points[1].value,0);assert.equal(departures.points[1].y,chart.zeroY);
  assert.equal(observedFlowCount(cell('2024',null)),null);
  assert.equal(observedFlowCount(cell('2024',99,'suppressed')),null);
  assert.equal(observedFlowCount(cell('2024',-1)),null);
});

test('zero counts are observations while completely missing, invalid-year and multiple-scope inputs create no marks', () => {
  const zeros=buildDemographicFlowPlot(flow('natural',[point('2025',0,0)]),292);
  assert.equal(zeros.hasData,true);assert.ok(zeros.maximum>0);
  assert.ok(zeros.components.every(component=>component.points[0].y===zeros.zeroY));
  for(const source of [flow('natural',[point('2025',null,null)]),flow('foreign',[point('undated',1,2)]),{...flow('foreign',[]),series:[]}]) {
    const chart=buildDemographicFlowPlot(source);
    assert.equal(chart.hasData,false);assert.ok(chart.components.every(component=>component.points.length===0));
  }
  const multiple=flow('foreign',[point('2025',1,2)]);multiple.series.push({...multiple.series[0],code:'064036'});
  assert.equal(buildDemographicFlowPlot(multiple).hasData,false);
});

test('provisional notes follow the source flag rather than a hard-coded latest year', () => {
  assert.equal(demographicFlowPeriodNote('Provisional (p)'),'Dato provvisorio indicato dalla fonte (p).');
  assert.equal(demographicFlowPeriodNote('See source information flag and release notes'),'Per questo periodo, la fonte rimanda alle proprie note di rilascio.');
  assert.equal(demographicFlowPeriodNote(undefined),'');
  assert.equal(demographicFlowPeriodNote('Other source note'),'Other source note');
});
