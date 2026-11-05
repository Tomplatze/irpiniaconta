import { snapshotObject, useSnapshotPublication } from '../utils/snapshot';
import { withDatabase } from '../utils/database';
import { readScope } from '../utils/scope';
/** Return the complete ten-section source registry with actual readiness. */
export default defineEventHandler(() => useSnapshotPublication() ? snapshotObject('catalogue.gz') : withDatabase(readScope));
