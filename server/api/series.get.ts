import { snapshotSeries } from '../utils/snapshot-legacy';
import { useSnapshotPublication } from '../utils/snapshot';
import { withDatabase } from '../utils/database';
import { series } from '../utils/measurements';
/** Return historical measurements for one to four exact municipal codes. */
export default defineEventHandler((event) => {
  const query = getQuery(event);
  if (typeof query.indicator !== 'string' || typeof query.codes !== 'string') throw createError({ statusCode: 400, statusMessage: 'Indicator and codes required' });
  const codes = query.codes.split(',');
  if (codes.length < 1 || codes.length > 4 || new Set(codes).size !== codes.length || codes.some((code) => !/^064\d{3}$/.test(code))) throw createError({ statusCode: 400, statusMessage: 'Invalid municipal codes' });
  if (useSnapshotPublication()) return snapshotSeries(query.indicator,codes);
  return withDatabase((database) => series(database, query.indicator as string, codes));
});
