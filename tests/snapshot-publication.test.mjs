import assert from 'node:assert/strict';
import { test } from 'node:test';

const base = process.env.ATLAS_TEST_URL || 'http://127.0.0.1:3011';

/** Check the emergency publication through the same HTTP routes used by the site. */
test('snapshot mode serves public data without a database connection', async () => {
  const health = await fetch(new URL('/api/health',base));
  assert.equal(health.status,200);
  const status = await health.json();
  assert.equal(status.source,'snapshot');
  assert.equal(status.municipalities,118);
  for (const path of ['/api/territory','/api/territory?code=064033','/api/territory?codes=064033,064036',
    '/api/municipal-records?code=064033&group=cohesion&view=index','/api/section-map',
    '/api/section?category=demography&metric=population','/api/collection','/api/catalogue',
    '/api/overview','/api/atlas','/api/health-statistics','/api/explore?indicator=population',
    '/api/series?indicator=population&codes=064033','/api/comparison?codes=064033,064036',
    '/api/entities?limit=1','/sitemap.xml']) {
    const response=await fetch(new URL(path,base));
    assert.equal(response.status,200,path);
    await response.arrayBuffer();
  }
});
