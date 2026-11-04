import assert from 'node:assert/strict';
import { test } from 'node:test';
import { cachedTerritory } from '../server/utils/territory-cache.ts';

test('coalesces concurrent reads, separates scopes and retries failures', async () => {
  let calls = 0;
  const read = async () => { calls++; return { generated_at: String(calls) }; };
  const [first, second] = await Promise.all([cachedTerritory('test-a', read), cachedTerritory('test-a', read)]);
  assert.equal(first, second);
  assert.equal(calls, 1);
  await cachedTerritory('test-b', read);
  assert.equal(calls, 2);
  await assert.rejects(cachedTerritory('test-error', async () => { throw new Error('unavailable'); }));
  await cachedTerritory('test-error', read);
  assert.equal(calls, 3);
});

test('expires cached results after one day', async () => {
  const original = Date.now;
  let now = 1000;
  Date.now = () => now;
  try {
    let calls = 0;
    const read = async () => ({ generated_at: String(++calls) });
    await cachedTerritory('test-expiry', read);
    now += 86399999;
    await cachedTerritory('test-expiry', read);
    assert.equal(calls, 1);
    now++;
    await cachedTerritory('test-expiry', read);
    assert.equal(calls, 2);
  } finally {
    Date.now = original;
  }
});
