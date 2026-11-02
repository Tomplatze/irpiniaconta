/** Source records available for review, independently of published indicators. */
export interface CollectedDataset {
  id: string;
  title: string;
  publisher: string;
  period_semantics: string;
  scope_ids: string[];
  job_ids: string[];
  coverage: number;
  municipality_codes: string[];
  record_count: number;
  periods: string[];
  fields: Record<string, string[]>;
  coverage_by_period: Record<string, number>;
  source_variables: string[];
  metadata_files: { path: string; label: string; sha256: string }[];
  notes: string;
  license: string | null;
  source_urls: string[];
  format: string;
  staging_file: string;
  staging_sha256: string;
}

/** One catalog scope entry, including incomplete or non-equivalent alternatives. */
export interface CollectionScope {
  id: string;
  category_id: string;
  title: string;
  publisher: string;
  landing_url: string;
  status: 'integrated' | 'collected' | 'alternative' | 'partial' | 'not_collected';
  product_integrated: boolean;
  dataset_ids: string[];
  coverage: number;
  periods: string[];
  assessment: string;
  ui_summary: string;
  blocker: string | null;
  available_product_fields: string[];
}

/** Locally generated inventory; numerical counts come from verified artifacts. */
export interface CollectionInventory {
  schema_version: number;
  generated_at: string;
  summary: {
    scope_count: number;
    product_integrated_count: number;
    scope_with_data_count: number;
    collected_dataset_families: number;
    collected_records: number;
    status_counts: Record<string, number>;
  };
  categories: { id: string; label: string; scope_count: number; with_data_count: number }[];
  sources: CollectionScope[];
  datasets: CollectedDataset[];
}
