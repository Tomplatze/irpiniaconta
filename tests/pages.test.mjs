import assert from 'node:assert/strict';
import {test} from 'node:test';
const base = process.env.ATLAS_TEST_URL || 'http://127.0.0.1:3000';
async function page(path) {
  const response = await fetch(new URL(path,base));
  assert.equal(response.status,200,path);
  return response.text();
}
async function publication(code) {
  const response = await fetch(new URL(`/api/territory${code ? '?code='+code : ''}`,base));
  assert.equal(response.status,200);
  return response.json();
}
function metricMarkup(html,id) {
  const result = html.match(new RegExp(`<article id="${id}"[^>]*>([\\s\\S]*?)<\\/article>`));
  assert.ok(result,`Missing metric ${id}`);
  return result[1];
}
const number = value => new Intl.NumberFormat('it-IT',{maximumFractionDigits:2}).format(value);

test('municipality profiles bind their own source values and retain a persistent geographical selection', async () => {
  const province = await publication();
  const provincePopulation = province.categories.flatMap(item=>item.metrics).find(item=>item.id==='population').series[0].current.value;
  for (const [code,name] of [['064033','Fontanarosa'],['064036','Gesualdo'],['064121','Montoro']]) {
    const data = await publication(code);
    const html = await page(`/comuni/${code}`);
    const population = data.categories.flatMap(item=>item.metrics).find(item=>item.id==='population').series[0].current.value;
    const heading = html.match(/<h1[^>]*>([\s\S]*?)<\/h1>/)?.[1].replace(/<!--[\s\S]*?-->/g,'');
    assert.ok(heading?.startsWith(name),`Wrong municipal heading for ${name}`);
    assert.match(html,new RegExp(`data-municipality="${code}"`));
    assert.match(html,new RegExp(`href="/comuni/${code}"[^>]*aria-label="${name}:[^"]*" aria-current="page"`));
    assert.match(html,/class="map-permanent-selection"/);
    assert.ok(metricMarkup(html,'population').includes(number(population)));
    assert.ok(!metricMarkup(html,'population').includes(number(provincePopulation)));
    assert.equal((html.match(/class="metric-story /g)||[]).length,45);
    assert.match(metricMarkup(html,'foreign_residents'),/Residenti con cittadinanza straniera/);
    const fruit = data.categories.find(item=>item.id==='agriculture').metrics.find(item=>item.id==='utilised_agricultural_area').breakdown.find(item=>item.metric.id==='breakdown_crops_fruit');
    assert.match(html,/Fruttiferi e frutta a guscio/);
    assert.match(html,/Fruttiferi: i censimenti storici/);
    assert.match(html,/brand-beta/);
    assert.match(metricMarkup(html,'waste_per_person'),/illustrations\/waste_per_person\.webp/);
    assert.match(html,/project-notice/);
    assert.match(html,/agenti di intelligenza artificiale/);
    assert.ok(html.includes(number(fruit.series[0].current.value)));
  }
});

test('all 118 official municipality links open dedicated routes and invalid identities do not fall back to Irpinia', async () => {
  const html = await page('/comuni');
  const data = await publication();
  for (const town of data.municipalities) assert.ok(html.includes(`href="/comuni/${town.code}"`),town.name);
  assert.equal(data.municipalities.length,118);
  for (const path of ['/comuni/064061','/comuni/064999','/sezioni/unknown','/sezioni/demography?code=064061']) {
    assert.equal((await fetch(new URL(path,base))).status,404,path);
  }
});

test('municipal crests match the registry and load locally', async () => {
  const response = await fetch(new URL('/api/municipal-crests', base));
  assert.equal(response.status, 200);
  const manifest = await response.json();
  const { municipalities } = await publication();
  assert.equal(manifest.records.length, municipalities.length);
  const byCode = new Map(manifest.records.map(record => [record.code, record]));
  assert.equal(byCode.size, 118);
  const html = await page('/comuni');
  for (const town of municipalities) {
    const crest = byCode.get(town.code);
    assert.equal(crest?.name, town.name);
    assert.match(crest.file, new RegExp(`^/municipal-crests/${town.code}\\.(?:png|jpe?g|gif|webp)$`, 'i'));
    assert.ok(html.includes(`src="${crest.file}"`), town.name);
  }
  for (let index = 0; index < municipalities.length; index += 10) {
    await Promise.all(municipalities.slice(index, index + 10).map(async town => {
      const image = await fetch(new URL(byCode.get(town.code).file, base));
      assert.equal(image.status, 200, town.name);
      assert.match(image.headers.get('content-type'), /^image\//);
      assert.ok((await image.arrayBuffer()).byteLength > 0, town.name);
    }));
  }
  const official = await page('/comuni/064033');
  const redrawn = await page('/comuni/064004');
  assert.match(official, /Stemma del Comune di Fontanarosa/);
  assert.match(redrawn, /Stemma del Comune di Aquilonia/);
  assert.doesNotMatch(redrawn, /<figcaption[^>]*>[^<]*Stemma ridisegnato/);
  assert.doesNotMatch(html, /class="municipal-crest-credit"/);
  assert.equal((await fetch(new URL('/api/municipal-crests/064061', base))).status, 404);
});

test('dedicated theme routes use the common metric template without leaking unrelated topics', async () => {
  const data = await publication('064033');
  for (const category of data.categories) {
    const html = await page(`/sezioni/${category.id}?code=064033`);
    assert.match(html,new RegExp(`id="tema-${category.id}"`));
    const nested = new Set(category.metrics.filter(metric=>metric.historical).map(metric=>metric.historical.metric.id));
    const stories = category.metrics.filter(metric=>!nested.has(metric.id));
    assert.equal((html.match(/class="metric-story /g)||[]).length,stories.length+(category.id==='agriculture' ? 1 : 0));
    for (const metric of stories) assert.ok(metricMarkup(html,metric.id));
    assert.match(html,/data-municipality="064033"/);
  }
});

test('supporting pages preserve honest status labels, official references and a table-free acquisition timeline', async () => {
  const sources = await page('/raccolta');
  const catalogue = await page('/dataset');
  const updates = await page('/aggiornamenti');
  for (const html of [sources,catalogue,updates]) {
    assert.match(html,/editorial-header/);
    assert.match(html,/project-notice/);
    assert.ok(!html.includes('<table'));
    assert.ok(!/href="\/api\/(?:export|section-export|collection-export)/.test(html));
  }
  assert.match(catalogue,/Catalogo delle fonti/);
  assert.match(catalogue,/Consulta l’elenco completo/);
  assert.match(sources,/Fonte del catalogo/);
  assert.doesNotMatch(sources,/Il contesto fa parte del dato/);
  assert.doesNotMatch(sources,/href="\/aggiornamenti/);
  assert.doesNotMatch(catalogue,/href="\/aggiornamenti/);
  assert.match(sources,/La stima delle persone residenti con cittadinanza straniera al 1° gennaio 2026/);
  assert.match(updates,/run-timeline/);
  assert.match(updates,/fonti con dati disponibili/i);
  assert.match(updates,/aggiornamenti automatici sono in pausa/i);
});

test('municipal stories contain local histories or snapshots and no inter-municipal plots',async()=>{
  const html=await page('/comuni/064033');
  assert.ok(!html.includes('class="latest-distribution"'));
  assert.ok(!html.includes('soil-area-visual'));
  assert.ok(!html.includes('map-tooltip'));
  assert.match(metricMarkup(html,'population'),/overlay-chart--area/);
  assert.ok(!metricMarkup(html,'asia_local_units').includes('breakdown-radar'));
  assert.match(html,/Le attività, settore per settore/);
  assert.match(html,/Commercio e riparazione di veicoli/);
  assert.match(html,/39 unità locali/);
  assert.match(html,/story-row--pair/);
  assert.ok(!metricMarkup(html,'utilised_agricultural_area').includes('breakdown-radar'));
  assert.match(html,/Le coltivazioni, da vicino/);
  assert.equal((html.match(/class="crop-profile-card"/g)||[]).length,15);
  assert.match(html,/Gli allevamenti, specie per specie/);
  assert.match(html,/Le coltivazioni biologiche, da vicino/);
  assert.doesNotMatch(html,/Grandi categorie di superficie/);
  assert.match(html,/Colture legnose e fruttiferi/);
  assert.match(html,/Cereali, legumi e ortaggi/);
  assert.match(html,/121,04 ha/);
  assert.match(html,/Non disponibile/);
  assert.match(html,/Nessun dato disponibile per i territori selezionati/);
  const comparison = await page('/confronta?codes=064033,064036');
  assert.match(comparison,/crop-radar__series--1/);
  assert.match(comparison,/scala del gruppo, comune ai territori selezionati/);
  for(const id of ['asia_local_units','asia_employees','municipal_service_spending','admin_historic_spending_per_person','solidarity_fund','waste_per_person','hot_days','frost_days','graduate_residents']) {
    const article=metricMarkup(html,id);
    assert.ok(!article.includes('overlay-chart'),id);
    assert.ok(article.includes('un solo dato') || article.includes('non abbiamo dati di altri anni'),id);
  }
  for(const id of ['pnrr_projects','cohesion_projects','digital_allocated_eur']) {
    const article=metricMarkup(html,id);
    assert.ok(!article.includes('<figure'),id);
  }
  assert.match(metricMarkup(html,'natural_balance'),/Nati vivi/);
  assert.match(metricMarkup(html,'natural_balance'),/Decessi/);
  assert.match(metricMarkup(html,'natural_balance'),/demographic-flow-chart--natural/);
  assert.match(metricMarkup(html,'foreign_migration_balance'),/demographic-flow-chart--foreign/);
});
