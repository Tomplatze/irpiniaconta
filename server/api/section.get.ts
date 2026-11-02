import { section, withSections } from '../utils/sections';
/** Return graphical history and the latest common source period for a declared section. */
export default defineEventHandler(event => {
  const query = getQuery(event);
  if (typeof query.category !== 'string' || query.metric !== undefined && typeof query.metric !== 'string'
    || query.code !== undefined && (typeof query.code !== 'string' || !/^064\d{3}$/.test(query.code))) {
    throw createError({ statusCode: 400, statusMessage: 'Invalid section selection' });
  }
  return withSections(database => section(database, query.category as string, query.metric as string | undefined, query.code as string | undefined ?? null));
});
