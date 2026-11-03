import assert from 'node:assert/strict';
import { readdir, readFile } from 'node:fs/promises';
import { test } from 'node:test';
import { HEALTH_PUBLICATION_READY } from '../app/utils/healthPublication.ts';

const base = process.env.ATLAS_TEST_URL || 'http://127.0.0.1:3189';

/** Fetch the production preview without following redirects. */
async function get(path) {
  return fetch(new URL(path, base), { redirect: 'manual' });
}

test('production route, navigation, catalogue and sitemap agree with the health release gate', async () => {
  const [health, home, catalogue, sitemap] = await Promise.all(['/salute', '/', '/raccolta', '/sitemap.xml'].map(get));
  assert.equal(health.status, HEALTH_PUBLICATION_READY ? 200 : 404);
  for (const response of [home, catalogue, sitemap]) assert.equal(response.status, 200);
  const [homeHtml, catalogueHtml, xml] = await Promise.all([home.text(), catalogue.text(), sitemap.text()]);
  assert.equal(/class="[^"]*health-nav-link/.test(homeHtml), HEALTH_PUBLICATION_READY);
  assert.equal(catalogueHtml.includes('PASSI · rapporto ASL Avellino'), HEALTH_PUBLICATION_READY);
  assert.equal(xml.includes('https://irpiniaconta.it/salute'), HEALTH_PUBLICATION_READY);
});

test('blocked production build does not ship the health draft in public JavaScript', { skip: HEALTH_PUBLICATION_READY }, async () => {
  const directory = new URL('../.output/public/_nuxt/', import.meta.url);
  const scripts = (await readdir(directory)).filter(file => file.endsWith('.js'));
  assert.ok(scripts.length, 'Build the application before running this test');
  for (const file of scripts) {
    const code = await readFile(new URL(file, directory), 'utf8');
    assert.doesNotMatch(code, /Speranza di vita alla nascita|Salute mentale e crescita/, `${file} contains draft health content`);
  }
});
