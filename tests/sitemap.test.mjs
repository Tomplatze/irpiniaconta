import assert from 'node:assert/strict';
import { test } from 'node:test';

const base = process.env.ATLAS_TEST_URL || 'http://127.0.0.1:3000';
const origin = 'https://irpiniaconta.it';

/** Fetch one local route without following redirects. */
async function get(path, headers = {}) {
  return fetch(new URL(path, base), { redirect: 'manual', headers });
}

test('sitemap contains the canonical live registry and excludes non-indexable routes', async () => {
  const [response, overviewResponse, robots] = await Promise.all([
    get('/sitemap.xml', { Host: 'untrusted.example' }), get('/api/sections'), get('/robots.txt'),
  ]);
  assert.equal(response.status, 200);
  assert.match(response.headers.get('content-type'), /^application\/xml/);
  assert.equal(overviewResponse.status, 200);
  assert.equal(robots.status, 200);
  const overview = await overviewResponse.json();
  const xml = await response.text();
  const urls = [...xml.matchAll(/<loc>(.*?)<\/loc>/g)].map(match => match[1]);
  const expected = [origin+'/', ...['comuni','confronta','raccolta'].map(path => `${origin}/${path}`),
    ...overview.municipalities.map(town => `${origin}/comuni/${town.code}`),
    ...overview.categories.map(category => `${origin}/sezioni/${category.id}`)];
  assert.match(xml, /^<\?xml version="1\.0" encoding="UTF-8"\?>\s*<urlset xmlns="http:\/\/www\.sitemaps\.org\/schemas\/sitemap\/0\.9">/);
  assert.match(xml, /<\/urlset>\s*$/);
  assert.equal(new Set(urls).size, urls.length);
  assert.deepEqual([...urls].sort(), expected.sort());
  assert.doesNotMatch(xml, /<lastmod>|untrusted\.example|\/privacy|\/dataset|\/aggiornamenti/);
  assert.ok(urls.every(url => !url.includes('?') && !url.includes('#')));
  assert.match(await robots.text(), /Sitemap: https:\/\/irpiniaconta\.it\/sitemap\.xml/);
  for (const path of ['/', '/comuni', '/confronta', '/raccolta', '/comuni/064033', '/comuni/064121',
    ...overview.categories.map(category => `/sezioni/${category.id}`)]) {
    const page = await get(path);
    assert.equal(page.status, 200, path);
    const html = await page.text();
    assert.ok(html.includes(`rel="canonical" href="${origin}${path}"`), `canonical ${path}`);
    assert.doesNotMatch(html, /<meta[^>]+name="robots"[^>]+noindex/i, path);
  }
});
