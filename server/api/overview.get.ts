import { snapshotObject, useSnapshotPublication } from '../utils/snapshot';
import { withDatabase } from '../utils/database';
import { readOverview } from '../utils/catalog';

/** Expose the verified local catalog and all 118 canonical municipality codes. */
export default defineEventHandler(() => useSnapshotPublication() ? snapshotObject('overview.gz') : withDatabase(readOverview));
