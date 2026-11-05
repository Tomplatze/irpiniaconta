import { snapshotObject, useSnapshotPublication } from '../utils/snapshot';
import { withDatabase } from '../utils/database';
import { readOverview } from '../utils/catalog';
import { readPublicationDocument } from '../utils/collection';

interface EditorialIndicator { id: string; label: string; description: string }
interface EditorialSelection { indicators: EditorialIndicator[] }

/** Present a small editorial selection while retaining complete data in the technical catalogue. */
export default defineEventHandler(() => useSnapshotPublication() ? snapshotObject('atlas.gz') : withDatabase(async database => {
  const overview = await readOverview(database);
  const selection = await readPublicationDocument<EditorialSelection>(database, 'editorial');
  const definitions = new Map(selection.indicators.map(indicator => [indicator.id, indicator]));
  const datasets = overview.datasets.map(dataset => ({ ...dataset,
    indicators: dataset.indicators.filter(indicator => definitions.has(indicator.id)).map(indicator => {
      const selected = definitions.get(indicator.id)!;
      return { ...indicator, label: selected.label, definition: selected.description };
    }),
  })).filter(dataset => dataset.indicators.length);
  return { ...overview, datasets };
}));
