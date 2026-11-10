const publicApiPaths = new Set([
  '/api/atlas', '/api/catalogue', '/api/collection', '/api/comparison',
  '/api/energy-statistics', '/api/entities', '/api/explore', '/api/health-statistics', '/api/municipal-records',
  '/api/overview', '/api/section', '/api/section-map', '/api/sections',
  '/api/series', '/api/territory', '/api/updates',
]);

/** Cache only successful public reads, with a bounded delay after ETL publication. */
export default defineNitroPlugin(nitro => {
  nitro.hooks.hook('beforeResponse', event => {
    const path = getRequestURL(event).pathname;
    if (event.method !== 'GET' || getResponseStatus(event) !== 200
      || !publicApiPaths.has(path) || getResponseHeader(event, 'set-cookie')) return;

    setResponseHeader(event, 'Netlify-CDN-Cache-Control', 'public, durable, max-age=2592000');
  });
});
