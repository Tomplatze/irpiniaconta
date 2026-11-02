import assert from 'node:assert/strict';
import { test } from 'node:test';
import { buildHistoryPlot } from '../app/utils/history.ts';

test('history leaves a real gap instead of connecting through null', () => {
  const plot=buildHistoryPlot([{period:'2021',value:10,status:'observed'},{period:'2022',value:null,status:'missing'},{period:'2023',value:12,status:'observed'}]);
  assert.equal(plot.points.length,2);assert.equal((plot.path.match(/M/g)||[]).length,2);
});

test('history uses actual time spacing and a finite scale for signed or constant data', () => {
  const plot=buildHistoryPlot([{period:'2016',value:-2,status:'observed'},{period:'2017',value:0,status:'observed'},{period:'2024',value:2,status:'observed'}]);
  assert.ok(plot.points[1].x-plot.points[0].x < plot.points[2].x-plot.points[1].x);
  assert.ok(plot.points.every(point=>Number.isFinite(point.x)&&Number.isFinite(point.y)));
  assert.equal(buildHistoryPlot([{period:'2024',value:3,status:'observed'}]).points[0].y,90);
});

import { buildOverlayPlot, buildMonthlyCalendar } from '../app/utils/history.ts';
test('overlaid municipalities use a common quantitative scale and common calendar positions',()=>{
  const a={code:'a',name:'A',values:[{period:'2016',value:10,status:'observed'},{period:'2024',value:20,status:'observed'}]};
  const b={code:'b',name:'B',values:[{period:'2016',value:100,status:'observed'},{period:'2024',value:200,status:'observed'}]};
  const plot=buildOverlayPlot([a,b]);
  assert.equal(plot.series[0].points[0].x,plot.series[1].points[0].x);
  assert.ok(plot.series[0].points[1].y>plot.series[1].points[0].y);
  assert.ok(plot.maximum>200 && plot.minimum<10);
  const narrow=buildOverlayPlot([a,b],320);
  assert.equal(narrow.minimum,plot.minimum);assert.equal(narrow.maximum,plot.maximum);
  assert.equal(narrow.series[0].points[1].y,plot.series[0].points[1].y);
  assert.ok(narrow.series.every(line=>line.points.every(point=>point.x>0 && point.x<320)));
});
test('an absent union period breaks an overlay instead of bridging missing observations',()=>{
  const plot=buildOverlayPlot([
    {code:'a',name:'A',values:[{period:'2020',value:10,status:'observed'},{period:'2022',value:12,status:'observed'}]},
    {code:'b',name:'B',values:[{period:'2020',value:-1,status:'observed'},{period:'2021',value:0,status:'observed'},{period:'2022',value:1,status:'observed'}]},
  ]);
  assert.equal((plot.series[0].path.match(/M/g)||[]).length,2);
  assert.ok(plot.series[1].points.every(point=>Number.isFinite(point.y)));
  assert.equal(buildOverlayPlot([{code:'a',name:'A',values:[{period:'undated',value:5,status:'observed'}]}]).series[0].points.length,0);
});

test('area and columns use a real zero baseline while preserving signed values and calendar spacing',()=>{
  const series=[{code:'a',name:'A',values:[{period:'2016',value:-2,status:'observed'},{period:'2017',value:0,status:'observed'},{period:'2024',value:8,status:'observed'}]}];
  const plot=buildOverlayPlot(series,420,{includeZero:true});
  const points=plot.series[0].points;
  assert.ok(plot.minimum<0 && plot.maximum>8);
  assert.ok(plot.ticks.includes(0));
  assert.equal(points[1].y,plot.zeroY);
  assert.ok(points[0].y>plot.zeroY && points[2].y<plot.zeroY);
  assert.ok(points[1].x-points[0].x<points[2].x-points[1].x);
  assert.ok(plot.barWidth<points[1].x-points[0].x);
  const positive=buildOverlayPlot([{code:'a',name:'A',values:[{period:'2023',value:100,status:'observed'},{period:'2024',value:200,status:'observed'}]}],420,{includeZero:true});
  assert.equal(positive.minimum,0);assert.equal(positive.zeroY,208);
  const negative=buildOverlayPlot([{code:'a',name:'A',values:[{period:'2023',value:-100,status:'observed'},{period:'2024',value:-200,status:'observed'}]}],420,{includeZero:true});
  assert.equal(negative.maximum,0);assert.equal(negative.zeroY,28);
  const zero=buildOverlayPlot([{code:'a',name:'A',values:[{period:'2024',value:0,status:'observed'}]}],320,{includeZero:true});
  assert.equal(zero.series[0].points[0].y,zero.zeroY);assert.ok(Number.isFinite(zero.zeroY));
});

test('filled areas close each observed segment separately and do not bridge gaps',()=>{
  const plot=buildOverlayPlot([{code:'a',name:'A',values:[
    {period:'2018',value:10,status:'observed'},{period:'2019',value:11,status:'observed'},
    {period:'2020',value:null,status:'missing'},
    {period:'2021',value:12,status:'observed'},{period:'2022',value:13,status:'observed'},
  ]}],600,{includeZero:true});
  assert.equal(plot.series[0].areaPaths.length,2);
  assert.equal((plot.series[0].path.match(/M/g)||[]).length,2);
  assert.ok(plot.series[0].areaPaths.every(path=>path.endsWith(' Z') && path.includes('208.00')));
  const absent=buildOverlayPlot([{code:'a',name:'A',values:[{period:'2024',value:null,status:'missing'}]}],320,{includeZero:true});
  assert.deepEqual(absent.series[0].areaPaths,[]);
});

test('line shading stays inside the chart when the vertical scale does not start at zero',()=>{
  const plot=buildOverlayPlot([{code:'a',name:'A',values:[
    {period:'2020',value:100,status:'observed'},{period:'2021',value:120,status:'observed'},
    {period:'2022',value:null,status:'missing'},
    {period:'2023',value:130,status:'observed'},{period:'2024',value:140,status:'observed'},
  ]}],600);
  assert.ok(plot.minimum>0);
  assert.equal(plot.series[0].areaPaths.length,2);
  assert.ok(plot.series[0].areaPaths.every(path=>path.includes('208.00') && path.endsWith(' Z')));
});

test('columns stay inside plot bounds at every viewport without changing actual calendar proportions',()=>{
  const series=[{code:'a',name:'A',values:[
    {period:'2016',value:-2,status:'observed'},
    {period:'2017',value:0,status:'observed'},
    {period:'2024',value:8,status:'observed'},
  ]}];
  for (const width of [320,420,720]) {
    const columns=buildOverlayPlot(series,width,{includeZero:true,bars:true});
    const points=columns.series[0].points;
    assert.ok(points.every(point=>point.x-columns.barWidth/2>=58 && point.x+columns.barWidth/2<=width-36));
    const ratio=(points[1].x-points[0].x)/(points[2].x-points[0].x);
    const realRatio=(Date.parse('2017-01-01')-Date.parse('2016-01-01'))/(Date.parse('2024-01-01')-Date.parse('2016-01-01'));
    assert.ok(Math.abs(ratio-realRatio)<1e-12);
    assert.ok(columns.barWidth<points[1].x-points[0].x);
    assert.equal(points[1].y,columns.zeroY);
    const area=buildOverlayPlot(series,width,{includeZero:true});
    assert.equal(area.series[0].points[0].x,54);
    assert.equal(area.series[0].points.at(-1).x,width-32);
    const single=buildOverlayPlot([{code:'a',name:'A',values:[{period:'2024',value:1,status:'observed'}]}],width,{includeZero:true,bars:true});
    assert.ok(single.series[0].points[0].x-single.barWidth/2>=58);
    assert.ok(single.series[0].points[0].x+single.barWidth/2<=width-36);
  }
});

test('monthly calendar uses the latest source year and preserves all twelve actual month positions',()=>{
  const calendar=buildMonthlyCalendar([
    {period:'2024-01',value:100,status:'observed'},
    {period:'2025-01',value:-3,status:'observed'},{period:'2025-03',value:0,status:'observed'},
    {period:'2025-04',value:null,status:'suppressed'},{period:'2025-07',value:25,status:'observed'},
    {period:'undated',value:200,status:'observed'},
  ]);
  assert.equal(calendar.year,'2025');assert.equal(calendar.cells.length,12);
  assert.equal(calendar.cells[0].period,'2025-01');assert.equal(calendar.cells[11].period,'2025-12');
  assert.equal(calendar.cells[1].fraction,null);assert.equal(calendar.cells[1].value,null);
  assert.equal(calendar.cells[3].status,'suppressed');assert.equal(calendar.cells[3].fraction,null);
  assert.equal(calendar.cells[2].value,0);assert.equal(calendar.cells[0].fraction,0);assert.equal(calendar.cells[6].fraction,1);
  assert.equal(calendar.minimum,-3);assert.equal(calendar.maximum,25);
  assert.equal(buildMonthlyCalendar([{period:'2025-01',value:4,status:'observed'}]).cells[0].fraction,.5);
  assert.deepEqual(buildMonthlyCalendar([{period:'undated',value:5,status:'observed'}]).cells,[]);
});
