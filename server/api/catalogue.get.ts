import { withDatabase } from '../utils/database';
import { readScope } from '../utils/scope';
/** Return the complete ten-section source registry with actual readiness. */
export default defineEventHandler(() => withDatabase(readScope));
