import { withDatabase } from '../utils/database';

const SITE_URL = 'https://irpiniaconta.it';

/** Publish canonical, indexable pages from the current read-only publication. */
export default defineEventHandler(async event => {
  const paths = await withDatabase(async database => {
    const towns = await database.query<{code: string}>('SELECT code FROM sections.municipalities ORDER BY code');
    const topics = await database.query<{id: string}>('SELECT id FROM sections.categories ORDER BY position');
    if (towns.rows.length !== 118 || !topics.rows.length ||
        towns.rows.some(row => !/^064\d{3}$/.test(row.code)) ||
        topics.rows.some(row => !/^[a-z][a-z0-9-]*$/.test(row.id))) {
      throw createError({statusCode: 503, statusMessage: 'Sitemap publication is incomplete.'});
    }
    return ['/', '/comuni', '/confronta', '/raccolta',
      ...towns.rows.map(row => `/comuni/${row.code}`),
      ...topics.rows.map(row => `/sezioni/${row.id}`)];
  }, 'sections');
  setHeader(event, 'Content-Type', 'application/xml; charset=utf-8');
  setHeader(event, 'Cache-Control', 'no-cache');
  const entries = paths.map(path => `  <url><loc>${SITE_URL}${path}</loc></url>`).join('\n');
  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${entries}\n</urlset>\n`;
});
