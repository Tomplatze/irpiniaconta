import { snapshotObject, useSnapshotPublication } from '../utils/snapshot';
import { withDatabase } from '../utils/database';
import type { HealthPublication } from '../../shared/health';
import { HEALTH_PUBLICATION_READY } from '../../app/utils/healthPublication';

/** Return the last complete health snapshot from the read-only publication database. */
export default defineEventHandler(() => {
  if (!import.meta.dev && !HEALTH_PUBLICATION_READY) throw createError({ statusCode: 404, statusMessage: 'Not found.' });
  if (useSnapshotPublication()) return snapshotObject<HealthPublication>('health.gz');
  return withDatabase(async database => {
  const result = await database.query<{ document: HealthPublication }>(
    'SELECT document FROM atlas.health_publications ORDER BY id DESC LIMIT 1',
  );
  const publication = result.rows[0]?.document;
  if (!publication || publication.version !== 1) {
    throw createError({ statusCode: 503, statusMessage: 'Health publication unavailable.' });
  }
    return publication;
  });
});
