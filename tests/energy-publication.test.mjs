import assert from 'node:assert/strict';
import { test } from 'node:test';

const base = process.env.ATLAS_TEST_URL || 'http://127.0.0.1:3000';

test('reviewed Terna data is provincial, correctly cited and present only on the homepage', async () => {
  const response = await fetch(new URL('/api/energy-statistics', base));
  assert.equal(response.status, 200);
  assert.equal(response.headers.get('Netlify-CDN-Cache-Control'), 'public, durable, max-age=2592000');
  const data = await response.json();
  assert.equal(data.scope, '064');
  assert.equal(data.unit, 'GWh');
  assert.deepEqual(data.years.slice(0, 7).map(row => row.year), [2018, 2019, 2020, 2021, 2022, 2023, 2024]);
  const row = data.years.find(item => item.year === 2024);
  assert.deepEqual(row.production, { hydro: 15.3, geothermal: null, solar: 158.8, wind: 1595.3, bioenergy: 4.9, total: 1774.4 });
  assert.deepEqual(row.consumption, { agriculture: 14.5, industry: 683, services: 380.8, domestic: 356.5, total: 1434.9 });
  assert.deepEqual(row.generation, { gross: 1893.3, auxiliaries: 26.9, net: 1866.4 });
  assert.equal(data.years[0].generation.net, 1422.9);
  assert.equal(row.source.generationPage, 186);
  assert.equal(row.source.productionPage, 187);
  assert.equal(row.source.consumptionPage, 189);
  assert.match(row.source.sha256, /^[0-9a-f]{64}$/);

  const catalogueResponse = await fetch(new URL('/api/catalogue', base));
  assert.equal(catalogueResponse.status, 200);
  const catalogue = await catalogueResponse.json();
  const energy = catalogue.provincial_sources.find(source => source.id === 'AMB-11');
  assert.equal(energy.period, '2018–2024');
  assert.equal(energy.license, null);
  assert.deepEqual(energy.tables.map(table => new URL(table.url).hash), ['#page=186', '#page=187', '#page=189']);
  const cataloguePage = await fetch(new URL('/raccolta', base));
  assert.equal(cataloguePage.status, 200);
  assert.match(await cataloguePage.text(), /Produzione e consumi elettrici nella provincia di Avellino/);

  for (const [path, visible] of [['/', true], ['/comuni/064033', false], ['/sezioni/environment', false]]) {
    const page = await fetch(new URL(path, base));
    assert.equal(page.status, 200, path);
    const html = await page.text();
    const section = html.match(/<article id="energia-irpinia"[\s\S]*?<\/article>/)?.[0];
    assert.equal(Boolean(section), visible, path);
    if (!section) continue;
    const environment = html.slice(html.indexOf('id="tema-environment"'));
    assert.match(environment, /<article id="energia-irpinia"/);
    assert.equal(environment.match(/<article id="([^"]+)"/)?.[1], 'energia-irpinia');
    assert.match(section, /<img[^>]+src="[^"]*renewable-energy[^"]*\.webp"/);
    assert.doesNotMatch(section, /<select\b/);
    assert.match(section, /431,5 GWh in più/);
    assert.match(section, /118,9 GWh/);
    assert.match(section, /Produzione netta, 2024: 1866,4 GWh/);
    const disclosure = section.match(/<details([^>]*)>\s*<summary[^>]*>Significato e fonti del dato<\/summary>[\s\S]*?<\/details>/);
    assert.ok(disclosure);
    assert.doesNotMatch(disclosure[1], /\bopen(?:[\s=]|$)/);
    assert.match(disclosure[0], /#page=186/);
    assert.match(disclosure[0], /scambi con la rete/);
    assert.doesNotMatch(section.replace(disclosure[0], ''), /tavola [567]|scambi con la rete|gigawattora/);
    assert.match(section, /energy-donut-ring/);
    assert.match(section, /energy-track/);
    assert.equal((section.match(/<svg[^>]*role="group"/g) ?? []).length, 3);
    const sourceChart = section.match(/<svg[^>]*aria-label="Variazione della produzione rinnovabile per fonte rispetto al 2018\.[^"]*"[\s\S]*?<\/svg>/)?.[0];
    assert.ok(sourceChart);
    assert.equal((sourceChart.match(/class="chart-series-line"/g) ?? []).length, 4);
    assert.doesNotMatch(sourceChart, /class="chart-bar/);
    assert.match(sourceChart, />-100%<\/text>/);
    assert.match(sourceChart, />\+100%<\/text>/);
    assert.match(sourceChart, /Fotovoltaico, 2018: 0%/);
    assert.match(sourceChart, /Fotovoltaico, 2024: \+76,1%/);
    assert.match(sourceChart, /Bioenergie, 2024: -91,7%/);
    assert.match(section, /158,8 GWh/);
    assert.match(section, /Servizi, 2019/);
    assert.doesNotMatch(section, /Servizi, 2018/);
  }
});
