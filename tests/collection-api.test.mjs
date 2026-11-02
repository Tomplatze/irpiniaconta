import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { gunzipSync } from 'node:zlib';
import { readFile } from 'node:fs/promises';
import { test } from 'node:test';

const base = process.env.ATLAS_TEST_URL || 'http://127.0.0.1:3000';

/** Verify evidence-backed availability, distinct from product-ready indicators. */
test('collection inventory accounts for every scope and measured coverage', async () => {
  const response = await fetch(new URL('/api/collection', base));
  assert.equal(response.status, 200);
  const inventory = await response.json();
  assert.equal(inventory.sources.length, 81);
  assert.equal(new Set(inventory.sources.map((source) => source.id)).size, 81);
  assert.equal(inventory.categories.length, 10);
  assert.equal(inventory.summary.scope_with_data_count, inventory.sources.filter((source) => source.product_integrated || source.dataset_ids.length).length);
  for (const dataset of inventory.datasets) {
    assert.equal(dataset.coverage, new Set(dataset.municipality_codes).size);
    assert.ok(dataset.municipality_codes.every((code) => /^064\d{3}$/.test(code)));
    assert.ok(Object.values(dataset.coverage_by_period).every((count) => count >= 0 && count <= 118));
  }
  const budget2024 = inventory.datasets.find((item) => item.id === 'bdap-budget-2024');
  const budget2025 = inventory.datasets.find((item) => item.id === 'bdap-budget-2025');
  assert.equal(budget2024.coverage, 118);
  assert.equal(budget2025.coverage, 117);
  assert.ok(!budget2025.municipality_codes.includes('064105'));
  assert.equal(inventory.datasets.find((item) => item.id === 'movimprese-province-2025').coverage, 0);
});

/** Private audit evidence remains exact even though the web download is retired. */
test('source provenance still identifies the retained original bytes', async () => {
  const inventory = await (await fetch(new URL('/api/collection', base))).json();
  const dataset = inventory.datasets.find(item => item.id === 'mef-participations-2023');
  assert.match(dataset.staging_file, /^data\/collection\/[a-zA-Z0-9_.-]+\.rows\.jsonl\.gz$/);
  const bytes = await readFile(new URL(`../${dataset.staging_file}`, import.meta.url));
  assert.equal(createHash('sha256').update(bytes).digest('hex'), dataset.staging_sha256);
  const rows = gunzipSync(bytes).toString('utf8').trim().split('\n').map(line => JSON.parse(line));
  assert.equal(rows.length,395);
  assert.ok(rows.every(row => row.period==='2023' && row.municipality_codes.length===1));
  assert.match(rows[0].source['Amministrazione Codice Fiscale'], /^\[\d{11}\]$/);
});

/** Retired endpoints never emit an attachment, including former metadata variants. */
test('all public dataset downloads are unavailable', async () => {
  for (const path of ['/api/export?indicator=births&period=2024', '/api/section-export?category=mobility&metric=empty_dwellings',
    '/api/collection-export?id=mef-participations-2023', '/api/collection-export?id=civitas-2023-ind-socnid-01-it&metadata=0',
    '/api/collection-export?id=../../config/sources.json']) {
    const response = await fetch(new URL(path,base));
    assert.equal(response.status,410);
    assert.equal(response.headers.get('content-disposition'),null);
    const body = await response.json();
    assert.equal(body.data.sourceCatalogue,'/raccolta');
  }
});
