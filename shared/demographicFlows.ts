import type { SectionPoint, SectionSource } from './sections';

/** Original event counts accompany, but never replace, the published net metric. */
export interface DemographicFlowPoint {
  period: string;
  positive: SectionPoint;
  negative: SectionPoint;
  balance: SectionPoint;
}

/** Provincial pairs share one complete cohort throughout the observed source years. */
export interface DemographicFlowSeries {
  code: string | null;
  name: string;
  scope: string;
  values: DemographicFlowPoint[];
}

/** Values stay non-negative; visual orientation distinguishes births/arrivals from deaths/departures. */
export interface DemographicFlow {
  kind: 'natural' | 'foreign';
  unit: 'persons';
  positive: { id: string; label: string };
  negative: { id: string; label: string };
  sources: SectionSource[];
  period_notes: Record<string, string>;
  series: DemographicFlowSeries[];
}
