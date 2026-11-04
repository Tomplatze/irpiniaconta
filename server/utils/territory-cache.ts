import type { TerritoryResponse } from '../../shared/sections';

const lifetime = 24 * 60 * 60 * 1000;
const maxEntries = 16;
const entries = new Map<string, { expires: number; value: Promise<TerritoryResponse> }>();

/** Share successful territory reads within one server instance for at most one day. */
export function cachedTerritory(key: string, read: () => Promise<TerritoryResponse>): Promise<TerritoryResponse> {
  const existing = entries.get(key);
  if (existing && existing.expires > Date.now()) {
    entries.delete(key);
    entries.set(key, existing);
    return existing.value;
  }
  entries.delete(key);
  const entry = { expires: Number.POSITIVE_INFINITY, value: Promise.resolve().then(read) };
  entries.set(key, entry);
  while (entries.size > maxEntries) entries.delete(entries.keys().next().value!);
  entry.value.then(() => { entry.expires = Date.now() + lifetime; }, () => {
    if (entries.get(key) === entry) entries.delete(key);
  });
  return entry.value;
}
