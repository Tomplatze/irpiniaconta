import { territory, withSections } from '../utils/sections';
import { cachedTerritory } from '../utils/territory-cache';
import { snapshotTerritory, useSnapshotPublication } from '../utils/snapshot';

/** Share the same definitions, periods and coverage across one to four scopes. */
export default defineEventHandler(event => {
  const query = getQuery(event);
  if (query.code !== undefined && query.codes !== undefined) throw createError({ statusCode: 400, statusMessage: 'Choose one scope selection' });
  const selection = query.codes ?? query.code;
  if (selection !== undefined && typeof selection !== 'string') throw createError({ statusCode: 400, statusMessage: 'Invalid scope selection' });
  const codes = typeof selection === 'string' ? selection.split(',') : [];
  if (query.codes !== undefined && codes.length < 2 || codes.length > 4 || codes.some(code => !/^064\d{3}$/.test(code)) || new Set(codes).size !== codes.length) {
    throw createError({ statusCode: 400, statusMessage: 'Select up to four distinct municipalities' });
  }
  return useSnapshotPublication() ? snapshotTerritory(codes) : cachedTerritory(codes.join(','), () => withSections(database => territory(database, codes)));
});
