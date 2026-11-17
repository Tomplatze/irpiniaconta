import { publicCacheKey, storePublicResponse } from '../utils/public-response-cache';

/** Cache only successful public reads, with a bounded delay after ETL publication. */
export default defineNitroPlugin(nitro => {
  nitro.hooks.hook('beforeResponse', (event, response) => {
    const key = publicCacheKey(getRequestURL(event));
    if (event.method !== 'GET' || getResponseStatus(event) !== 200
      || !key || getResponseHeader(event, 'set-cookie')) return;

    setResponseHeader(event, 'Netlify-CDN-Cache-Control', 'public, durable, max-age=2592000');
    if (useRuntimeConfig().publicationMode !== 'database' || !useRuntimeConfig().publicResponseCacheEnabled || getRequestHeader(event, 'authorization')
      || getRequestHeader(event, 'cookie') || getResponseHeader(event, 'X-Public-Cache')) return;
    if (response.body === null || typeof response.body !== 'object' || ArrayBuffer.isView(response.body)) return;
    if (storePublicResponse(key, response.body)) setResponseHeader(event, 'X-Public-Cache', 'MISS');
  });
});
