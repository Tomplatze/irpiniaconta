import { snapshotObject, useSnapshotPublication } from '../utils/snapshot';
import type { SectionMap } from '../../shared/sections';
import { readPublicationDocument } from '../utils/collection';
import { withDatabase } from '../utils/database';
/** Serve display-only simplified official boundaries with no external map requests. */
export default defineEventHandler(() => useSnapshotPublication() ? snapshotObject<SectionMap>('section_map.gz') : withDatabase((database) => readPublicationDocument<SectionMap>(database, 'sections-map')));
