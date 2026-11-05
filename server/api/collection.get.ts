import { snapshotObject, useSnapshotPublication } from '../utils/snapshot';
import { readCollection } from '../utils/collection';
import { withDatabase } from '../utils/database';

/** Return actual collected source families, fields, periods and open blockers. */
export default defineEventHandler(() => useSnapshotPublication() ? snapshotObject('collection.gz') : withDatabase(readCollection));
