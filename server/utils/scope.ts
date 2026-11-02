import type { PoolClient } from 'pg';
import type { Catalogue, Category, SourceEntry, EntityRecord } from '../../shared/catalogue';
import { readCatalog } from './catalog';

/** Overlay configured scope with measured ingestion state; unknown licences remain unknown. */
export async function readScope(database: PoolClient): Promise<Catalogue> {
  const datasets = await readCatalog(database);
  const registry = await database.query<Record<string, unknown>>('SELECT metadata::text AS metadata FROM source_registry ORDER BY position');
  const storedCategories = await database.query<Record<string, unknown>>('SELECT metadata::text AS metadata FROM categories ORDER BY position');
  const counts = await database.query<Record<string, unknown>>('SELECT dataset_id,COUNT(*) AS total,COUNT(municipality_code) AS associated FROM entities GROUP BY dataset_id');
  const sources = registry.rows.map((row): SourceEntry => {
    const configured = JSON.parse(String(row.metadata)) as SourceEntry;
    const dataset = datasets.find(item => item.id === (configured.dataset_id || configured.id)) ?? null;
    const details = dataset as typeof dataset & { last_attempt?: { at?: string; status?: string; blocker?: string; landing_check?: { status: string } }; stale?: boolean };
    const count = counts.rows.find(item => item.dataset_id === dataset?.id);
    return { ...configured, dataset, status: dataset?.status === 'ready' ? 'ready' : configured.status === 'restricted' ? 'restricted' : configured.adapter ? 'blocked' : 'pending',
      blocker: dataset?.status === 'ready' ? null : dataset?.blocker || configured.blocker, update_error: details?.stale ? details.last_attempt?.blocker ?? null : null, stale: details?.stale ?? false,
      checked_at: details?.last_attempt?.at ?? null, landing_status: details?.last_attempt?.landing_check?.status ?? null,
      entity_count: Number(count?.total ?? 0), associated_entity_count: Number(count?.associated ?? 0) };
  });
  const categories = storedCategories.rows.map((row): Category => {
    const category = JSON.parse(String(row.metadata)) as Category;
    const entries = sources.filter(source => source.category_id === category.id);
    return { ...category, ready_count: entries.filter(source => source.status === 'ready').length,
      blocked_count: entries.filter(source => source.status !== 'ready').length };
  });
  return { categories, sources };
}

/** Convert stored JSON into a typed, escaped-by-Vue public entity record. */
export function entityRecord(row: Record<string, unknown>): EntityRecord {
  return { dataset_id: String(row.dataset_id), source_id: String(row.source_id),
    municipality_code: row.municipality_code === null ? null : String(row.municipality_code),
    title: String(row.title), kind: String(row.kind), period: String(row.period),
    payload: JSON.parse(String(row.payload)) as Record<string, unknown>,
    municipality_name: row.municipality_name === null ? null : String(row.municipality_name) };
}
