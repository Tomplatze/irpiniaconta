import { withDatabase } from '../utils/database';
import { readOverview } from '../utils/catalog';

/** Expose the verified local catalog and all 118 canonical municipality codes. */
export default defineEventHandler(() => withDatabase(readOverview));
