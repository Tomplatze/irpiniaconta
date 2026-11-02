import { readCollection } from '../utils/collection';
import { withDatabase } from '../utils/database';

/** Return actual collected source families, fields, periods and open blockers. */
export default defineEventHandler(() => withDatabase(readCollection));
