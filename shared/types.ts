/** Public read-only contracts shared between the local API and presentation. */
export type ValueStatus = 'observed' | 'missing' | 'suppressed' | 'unavailable';

export interface Municipality { code: string; name: string; province_code: string; region_code: string }

export interface Artifact {
  url: string; resolved_url: string; http_status: number; content_type: string | null;
  bytes: number; sha256: string; retrieved_at: string; filename: string;
  method?: 'GET' | 'POST'; request_body?: unknown; request_sha256?: string;
}

export interface Indicator {
  id: string; dataset_id: string; label: string; unit: string; definition: string;
  periods: string[]; latest_period: string | null; observed_count: number;
  suppressed_count: number; missing_count: number; absent_count: number;
}

export interface Dataset {
  id: string; name: string; publisher: string; landing_url: string; download_url: string | null;
  license: string | null; license_url: string | null; format: string; geography: string;
  period: string; status: 'ready' | 'blocked'; blocker: string | null; notes: string | string[];
  verified_at: string; artifacts: Artifact[]; indicators: Indicator[];
}

export interface Overview {
  municipalities: Municipality[]; datasets: Dataset[];
  summary: { municipality_count: number; ready_sources: number; total_sources: number;
    observation_count: number; last_run: string; acquired_at: string; mode: string };
}

export interface Measurement {
  code: string; name: string; value: number | null; status: ValueStatus;
}

export interface ComparisonRow {
  indicator: Indicator; dataset_id: string; period: string | null; measurements: Measurement[];
}

export interface Comparison { municipalities: Municipality[]; rows: ComparisonRow[] }
