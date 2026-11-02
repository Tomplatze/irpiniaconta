import { sectionOverview, withSections } from '../utils/sections';
/** Supply the curated section catalogue at provincial or municipal scope. */
export default defineEventHandler(event => {
  const query = getQuery(event);
  if (query.code !== undefined && (typeof query.code !== 'string' || !/^064\d{3}$/.test(query.code))) throw createError({ statusCode: 400, statusMessage: 'Invalid municipal code' });
  return withSections(database => sectionOverview(database, query.code as string | undefined ?? null));
});
