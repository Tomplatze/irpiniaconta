import type { Catalogue, ProvincialSourceEntry } from '../../shared/catalogue';
import sourceRegistry from '../../config/sources.json';
import { snapshotObject, useSnapshotPublication } from '../utils/snapshot';
import { withDatabase } from '../utils/database';
import { readScope } from '../utils/scope';

/** Supplement the municipality-oriented inventory with the reviewed provincial source. */
function energySource(): ProvincialSourceEntry {
  const { id, title, publisher, landing_url, description, license, options } = sourceRegistry.provincial_publications.energy;
  const reports = Object.entries(options.reports).sort(([a], [b]) => a.localeCompare(b));
  const [year, report] = reports.at(-1)!;
  return {
    id, title, publisher, landing_url, description, license,
    period: `${reports[0]![0]}–${year}`,
    rights_url: options.rights_url,
    tables: [
      { label: `Produzione totale ${year} · tavola 5`, url: `${report.url}#page=${report.generation_page}` },
      { label: `Rinnovabili ${year} · tavola 6`, url: `${report.url}#page=${report.production_page}` },
      { label: `Consumi ${year} · tavola 7`, url: `${report.url}#page=${report.consumption_page}` },
    ],
  };
}

/** Return the catalogue from the active publication, with current source references. */
export default defineEventHandler(async (): Promise<Catalogue> => {
  const catalogue = await (useSnapshotPublication() ? snapshotObject<Catalogue>('catalogue.gz') : withDatabase(readScope));
  return { ...catalogue, provincial_sources: [energySource()] };
});
