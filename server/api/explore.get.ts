import { snapshotExplore } from '../utils/snapshot-legacy';
import { useSnapshotPublication } from '../utils/snapshot';
import { withDatabase } from '../utils/database';
import { explore } from '../utils/measurements';
/** Explore one registered indicator and one explicit period across all 118 municipalities. */
export default defineEventHandler((event) => {
  const query = getQuery(event);
  if (typeof query.indicator !== 'string' || (query.period !== undefined && typeof query.period !== 'string')) throw createError({ statusCode: 400, statusMessage: 'Invalid indicator or period' });
  if (useSnapshotPublication()) return snapshotExplore(query.indicator,query.period as string | undefined);
  return withDatabase((database) => explore(database, query.indicator as string, query.period as string | undefined));
});
