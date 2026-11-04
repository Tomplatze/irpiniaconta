import assert from 'node:assert/strict';
import { test } from 'node:test';

globalThis.defineNitroPlugin = callback => callback;
globalThis.getRequestURL = event => new URL(event.url);
globalThis.getResponseStatus = event => event.status;
globalThis.getResponseHeader = (event, name) => event.headers[name];
globalThis.setResponseHeader = (event, name, value) => { event.headers[name] = value; };
const { default: plugin } = await import('../server/plugins/public-cache.ts');
let hook;
plugin({ hooks: { hook: (_name, callback) => { hook = callback; } } });

test('only successful public GET responses receive a bounded CDN cache policy', () => {
  const event = (path, status = 200, method = 'GET', headers = {}) => ({ url: `https://example.test${path}`, status, method, headers });
  const good = event('/api/territory?code=064033');
  hook(good);
  assert.equal(good.headers['Netlify-CDN-Cache-Control'], 'public, durable, max-age=300');
  for (const candidate of [event('/api/territory', 503), event('/api/territory', 200, 'POST'),
    event('/api/health'), event('/'), event('/api/territory', 200, 'GET', { 'set-cookie': 'session=value' })]) {
    hook(candidate);
    assert.equal(candidate.headers['Netlify-CDN-Cache-Control'], undefined);
  }
});
