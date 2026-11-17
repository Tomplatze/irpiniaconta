import assert from 'node:assert/strict';
import { test } from 'node:test';
import { publicCacheKey, readPublicResponse, storePublicResponse } from '../server/utils/public-response-cache.ts';

test('public cache isolates queries and expires responses after 30 days', () => {
  const first = publicCacheKey(new URL('https://example.test/api/sections?code=064033'));
  const second = publicCacheKey(new URL('https://example.test/api/sections?code=064036'));
  assert.ok(first && second);
  assert.notEqual(first, second);
  assert.equal(publicCacheKey(new URL('https://example.test/api/health')), undefined);
  const originalNow = Date.now;
  try {
    Date.now = () => 1_000;
    storePublicResponse(first, { value: 1 });
    assert.equal(readPublicResponse(first), '{"value":1}');
    assert.equal(readPublicResponse(second), undefined);
    Date.now = () => 1_000 + 30 * 24 * 60 * 60 * 1000;
    assert.equal(readPublicResponse(first), undefined);
  } finally { Date.now = originalNow; }
});

test('public cache rejects oversized responses and evicts old entries', () => {
  storePublicResponse('oversized', { value: 'x'.repeat(4 * 1024 * 1024) });
  assert.equal(readPublicResponse('oversized'), undefined);
  for (let index = 0; index < 257; index++) storePublicResponse(`entry-${index}`, { index });
  assert.equal(readPublicResponse('entry-0'), undefined);
  assert.equal(readPublicResponse('entry-256'), '{"index":256}');
});
