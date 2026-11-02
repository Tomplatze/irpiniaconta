import type { SectionMap } from '../../shared/sections';
import { readPublicationDocument } from '../utils/collection';
import { withDatabase } from '../utils/database';
/** Serve display-only simplified official boundaries with no external map requests. */
export default defineEventHandler(() => withDatabase((database) => readPublicationDocument<SectionMap>(database, 'sections-map')));
