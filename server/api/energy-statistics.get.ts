import type { EnergyPublication } from '../../shared/energy';
import { withDatabase } from '../utils/database';
import { snapshotObject, useSnapshotPublication } from '../utils/snapshot';

/** Read the reviewed provincial series from the configured publication source. */
export default defineEventHandler(async () => {
  let publication: EnergyPublication | undefined;
  if (useSnapshotPublication()) {
    if (!useRuntimeConfig().energyPublicationReady) {
      throw createError({ statusCode: 404, statusMessage: 'Energy publication not enabled.' });
    }
    publication = await snapshotObject<EnergyPublication>('energy.gz');
  } else {
    publication = await withDatabase(async database => {
      const result = await database.query<{ document: EnergyPublication }>(
        'SELECT document FROM atlas.energy_publications ORDER BY id DESC LIMIT 1',
      );
      return result.rows[0]?.document;
    });
  }

  if (publication?.version !== 1 || publication.scope !== '064' || publication.unit !== 'GWh'
    || !Array.isArray(publication.years) || !publication.years.length) {
    throw createError({ statusCode: 503, statusMessage: 'Energy publication unavailable.' });
  }
  return publication;
});
