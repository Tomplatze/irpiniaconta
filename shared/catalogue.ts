import type { Dataset, Indicator, Municipality, ValueStatus } from './types';

/** Ten editorial sections backed by the central source registry. */
export interface Category { id: string; label: string; expected_items: number; ready_count: number; blocked_count: number }
/** Readiness is evidence from ingestion; publisher-page reachability is reported separately. */
export interface SourceEntry {
  id: string; category_id: string; title: string; publisher: string; landing_url: string;
  geography: string; dataset_id: string | null; status: 'ready' | 'blocked' | 'pending' | 'restricted';
  blocker: string | null; adapter: string | null; update_error: string | null; cadence_days: number; update_policy: string;
  dataset: Dataset | null; stale: boolean; checked_at: string | null;
  landing_status: string | null; entity_count: number; associated_entity_count: number;
}
export interface ProvincialSourceEntry {
  id: string;
  title: string;
  publisher: string;
  landing_url: string;
  description: string;
  period: string;
  rights_url: string;
  license: string | null;
  tables: Array<{ label: string; url: string }>;
}
export interface Catalogue { categories: Category[]; sources: SourceEntry[]; provincial_sources?: ProvincialSourceEntry[] }
export interface EntityRecord {
  dataset_id: string; source_id: string; municipality_code: string | null; title: string;
  kind: string; period: string; payload: Record<string, unknown>; municipality_name: string | null;
}
export interface EntityPage { total: number; records: EntityRecord[]; limit: number; offset: number }
export interface SeriesPoint { period: string; value: number | null; status: ValueStatus }
export interface Series { indicator: Indicator; dataset: Dataset; municipalities: Array<Municipality & { values: SeriesPoint[] }> }
export interface Exploration { indicator: Indicator; period: string; values: Array<Municipality & { value: number | null; status: ValueStatus }> }
export interface RunSummary { id: string; completed_at: string; mode: string; attempted: number; failed: number; ready: number }
