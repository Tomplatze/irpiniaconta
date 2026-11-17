import { publicCacheKey, readPublicResponse } from '../utils/public-response-cache';

/** Serve anonymous public reads from the bounded VPS cache in database mode. */
export default defineEventHandler(event => {
  if (useRuntimeConfig().publicationMode !== 'database' || !useRuntimeConfig().publicResponseCacheEnabled || event.method !== 'GET'
    || getRequestHeader(event, 'authorization') || getRequestHeader(event, 'cookie')) return;
  const key = publicCacheKey(getRequestURL(event));
  if (!key) return;
  const body = readPublicResponse(key);
  if (body === undefined) return;
  setResponseHeader(event, 'Content-Type', 'application/json; charset=utf-8');
  setResponseHeader(event, 'X-Public-Cache', 'HIT');
  return body;
});
