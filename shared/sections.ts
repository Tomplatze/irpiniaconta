import type { ValueStatus } from './types';
import type { DemographicFlow } from './demographicFlows';

/** Public metric semantics, provenance and current-period coverage. */
export interface SectionSource {
  id: string; title: string; publisher: string; url: string; license: string | null;
  verified_at: string; staging_sha256?: string;
}
export type AggregateMethod = 'sum' | 'weighted_mean' | 'mean' | 'median' | 'distinct';
export interface SectionMetric {
  id: string; category: string; label: string; description: string; unit: string;
  aggregation: AggregateMethod; periods: string[]; latest_period: string;
  sources: SectionSource[]; has_monthly: boolean;
}
export interface SectionPoint { period: string; value: number | null; status: ValueStatus; coverage: number }
export interface SectionCurrent extends SectionPoint { scope: string; summary_label: string }
export interface SectionSummaryMetric extends SectionMetric { current: SectionCurrent }
export interface SectionDefinition { id: string; label: string; intro: string; primary: string; headline: string }
export interface SectionSummary extends SectionDefinition { metrics: SectionSummaryMetric[] }
export interface SectionOverview {
  generated_at: string; categories: SectionSummary[]; municipalities: Array<{ code: string; name: string }>;
  metric_count: number;
}
export interface SectionHistory { scope: string; label: string; values: SectionPoint[] }
export interface SectionMeasurement { code: string; name: string; value: number | null; status: ValueStatus }
export interface SectionResponse {
  category: SectionDefinition; metrics: SectionSummaryMetric[]; metric: SectionMetric;
  code: string | null; current: SectionCurrent; history: SectionHistory;
  related_history: SectionHistory | null; monthly: SectionHistory | null;
  distribution: SectionMeasurement[]; municipalities: Array<{ code: string; name: string }>;
}
export interface SectionMap { view_box: string; features: Array<{ code: string; path: string }>; source: string; source_sha256: string }

/** One publication contract for provincial, municipal and overlaid comparison views. */
export interface TerritorySeries {
  code: string | null; name: string; current: SectionCurrent;
  history: SectionHistory; monthly: SectionHistory | null;
}
export interface TerritoryMetric extends SectionMetric {
  series: TerritorySeries[]; distribution: SectionMeasurement[];
  demographic_flow?: DemographicFlow;
  historical?: MetricHistoryCompanion;
  breakdown?: Array<{ metric: SectionMetric; series: Array<{ code: string | null; name: string; current: SectionCurrent }>; historical?: MetricHistoryCompanion }>;
}
/** Keep related historical definitions, periods and provenance separate from the latest source. */
export interface MetricHistoryCompanion {
  metric: SectionMetric;
  series: Array<{code: string | null; name: string; history: SectionHistory}>;
}
export interface TerritoryCategory extends SectionDefinition { metrics: TerritoryMetric[] }
export interface TerritoryResponse {
  generated_at: string; categories: TerritoryCategory[];
  municipalities: Array<{ code: string; name: string }>;
  scopes: Array<{ code: string | null; name: string }>;
}
