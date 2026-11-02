import type { MetricHistoryCompanion, SectionMetric, TerritoryMetric } from '../../shared/sections';

export type MetricVisual = 'history' | 'flows' | 'percentage' | 'counter' | 'distribution';
export type HistoryVariant = 'line' | 'area' | 'bars';
export interface HistoryPresentation extends MetricHistoryCompanion { separate: boolean }

/** Historical lines need multiple observed periods; a single observation never becomes a trend. */
function hasHistory(series: MetricHistoryCompanion['series']): boolean {
  return series.some(item => item.history.values.filter(point => point.status==='observed' && point.value!==null).length>1);
}

/** A related census remains a separately named series, with its own periods and provenance. */
export function historyPresentation(metric: TerritoryMetric): HistoryPresentation | null {
  const series = metric.series.map(item => ({code:item.code,name:item.name,history:item.history}));
  if (hasHistory(series)) return {metric,series,separate:false};
  if (metric.historical && hasHistory(metric.historical.series)) return {...metric.historical,separate:true};
  return null;
}

/** Match historical geometry to the source being drawn; municipal comparisons retain overlaid lines. */
export function historyVariant(metric: TerritoryMetric): HistoryVariant {
  if (metric.series.length!==1) return 'line';
  const id = historyPresentation(metric)?.metric.id ?? metric.id;
  if (['natural_balance','foreign_migration_balance','soil_net_change_ha'].includes(id)) return 'bars';
  if (['resident_population_history','historic_agricultural_holdings','private_households'].includes(id)) return 'area';
  return 'line';
}

/** Single-territory pages describe their own history, never the distribution of other municipalities. */
export function metricVisual(metric: TerritoryMetric): MetricVisual {
  if (metric.category==='culture' || metric.category==='investments' || metric.id==='pharmacy_location_count') return 'counter';
  if (metric.demographic_flow && metric.series.length===1) return 'flows';
  if (historyPresentation(metric)) return 'history';
  if (metric.unit==='%' && metric.series.length===1) return 'percentage';
  return metric.series.length>1 ? 'distribution' : 'counter';
}

/** Display clearer question-specific labels without changing the published metric identity. */
export function metricTitle(metric: TerritoryMetric): string {
  if (metric.demographic_flow && metric.series.length===1) return metric.demographic_flow.kind==='natural' ? 'Nati e morti' : 'Arrivi e partenze dall’estero';
  if (metric.id==='natural_balance') return 'Saldo naturale · nati meno decessi';
  if (metric.id==='foreign_migration_balance') return 'Saldo con l’estero · arrivi meno partenze';
  if (metric.id==='soil_consumed_ha') return 'Superficie di suolo consumato';
  return metric.label;
}

/** Keep sources from a separately drawn historical definition available in the same evidence panel. */
export function storySources(metric: TerritoryMetric): SectionMetric['sources'] {
  const sources = [...metric.sources,...(metric.historical?.metric.sources ?? []),...(metric.demographic_flow?.sources ?? []),...(metric.breakdown?.flatMap(item => item.metric.sources) ?? [])];
  return [...new Map(sources.map(source => [`${source.id}:${source.url}`,source])).values()];
}

/** A public historical companion stays inside its latest-data story instead of duplicating a card. */
export function visibleStoryMetrics(metrics: TerritoryMetric[]): TerritoryMetric[] {
  const companions = new Set(metrics.flatMap(metric => metric.historical ? [metric.historical.metric.id] : []));
  return metrics.filter(metric => !companions.has(metric.id));
}

/** Each cell represents one percentage point; fractional cells retain the exact published rate. */
export function percentageCells(value: number | null): number[] | null {
  if (value===null || !Number.isFinite(value) || value<0 || value>100) return null;
  return Array.from({length:100},(_,index) => Math.max(0,Math.min(1,value-index)));
}

/** Reuse source-authored publisher names without inventing an editorial attribution. */
export function sourcePublishers(metric: TerritoryMetric): string {
  return [...new Set(storySources(metric).map(source => source.publisher))].join(' · ');
}
