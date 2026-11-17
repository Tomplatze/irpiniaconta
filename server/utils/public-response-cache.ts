const publicPaths = new Set([
  '/api/atlas', '/api/catalogue', '/api/collection', '/api/comparison',
  '/api/energy-statistics', '/api/entities', '/api/explore', '/api/health-statistics', '/api/municipal-records',
  '/api/overview', '/api/section', '/api/section-map', '/api/sections',
  '/api/series', '/api/territory', '/api/updates',
]);

const lifetime = 30 * 24 * 60 * 60 * 1000;
const maxBytes = 64 * 1024 * 1024;
const maxEntryBytes = 4 * 1024 * 1024;
const maxEntries = 256;
const entries = new Map<string, { body: string; bytes: number; expires: number }>();
let totalBytes = 0;

/** Return a bounded key only for explicitly public API routes. */
export function publicCacheKey(url: URL): string | undefined {
  const key = url.pathname + url.search;
  return publicPaths.has(url.pathname) && key.length <= 2048 ? key : undefined;
}

/** Read and refresh the least-recently-used position of a live response. */
export function readPublicResponse(key: string): string | undefined {
  const entry = entries.get(key);
  if (!entry) return;
  entries.delete(key);
  if (entry.expires <= Date.now()) { totalBytes -= entry.bytes; return; }
  entries.set(key, entry);
  return entry.body;
}

/** Store a JSON response within fixed per-process memory and entry limits. */
export function storePublicResponse(key: string, value: unknown): boolean {
  let body: string | undefined;
  try { body = JSON.stringify(value); } catch { return false; }
  if (body === undefined) return false;
  const bytes = Buffer.byteLength(body);
  if (bytes > maxEntryBytes) return false;
  const previous = entries.get(key);
  if (previous) { totalBytes -= previous.bytes; entries.delete(key); }
  while (entries.size && (entries.size >= maxEntries || totalBytes + bytes > maxBytes)) {
    const oldest = entries.keys().next().value;
    if (oldest === undefined) break;
    totalBytes -= entries.get(oldest)!.bytes;
    entries.delete(oldest);
  }
  entries.set(key, { body, bytes, expires: Date.now() + lifetime });
  totalBytes += bytes;
  return true;
}
