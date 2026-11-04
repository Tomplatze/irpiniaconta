import type { PoolClient } from 'pg';
import { withDatabase } from './database';
import type { AggregateMethod, SectionCurrent, SectionDefinition, SectionHistory, SectionMetric, SectionOverview, SectionPoint, SectionResponse, SectionSource, SectionSummaryMetric } from '../../shared/sections';
import type { ValueStatus } from '../../shared/types';
import type { TerritoryMetric, TerritoryResponse } from '../../shared/sections';
import { getDemographicFlows } from './demographicFlows';

interface StoredMetric extends SectionMetric { presentation_role?: 'public' | 'supporting_history' | 'supporting_breakdown'; breakdown_parent?: string; regional_distinct?: Record<string, number>; recipe: { related_history?: string; show_companion_history?: boolean } }
interface Cell { code: string; period: string; value: number | null; status: ValueStatus; weight: number | null }
const methodLabels: Record<AggregateMethod, string> = {
  sum: 'Totale dei comuni con dato', weighted_mean: 'Media ponderata con il denominatore della fonte',
  mean: 'Media dei punti di campionamento', median: 'Mediana dei comuni con dato', distinct: 'Elementi distinti nella raccolta',
};

/** Read the curated publication through the same bounded PostgreSQL pool. */
export function withSections<T>(callback: (database: PoolClient) => Promise<T>): Promise<T> {
  return withDatabase(callback, 'sections');
}

/** Read only internally generated metadata; original source fields stay outside presentation. */
async function metrics(database: PoolClient, category?: string): Promise<StoredMetric[]> {
  const result = category
    ? await database.query<Record<string, unknown>>('SELECT metadata::text AS metadata FROM metrics WHERE category=$1 ORDER BY position', [category])
    : await database.query<Record<string, unknown>>('SELECT metadata::text AS metadata FROM metrics ORDER BY position');
  return result.rows.map(row => JSON.parse(String(row.metadata)) as StoredMetric);
}
async function towns(database: PoolClient): Promise<Array<{ code: string; name: string }>> {
  const result = await database.query<Record<string, unknown>>('SELECT code,name FROM municipalities ORDER BY lower(name),name,code');
  return result.rows.map(row => ({ code: String(row.code), name: String(row.name) }));
}
async function categories(database: PoolClient): Promise<SectionDefinition[]> {
  const result = await database.query<Record<string, unknown>>('SELECT metadata::text AS metadata FROM categories ORDER BY position');
  return result.rows.map(row => JSON.parse(String(row.metadata)) as SectionDefinition);
}

/** Project authored public fields explicitly, excluding ETL rules and internal paths. */
function publicMetric(metric: StoredMetric): SectionMetric {
  const sources: SectionSource[] = metric.sources.map(source => ({ id: source.id, title: source.title, publisher: source.publisher, url: source.url,
    license: source.license, verified_at: source.verified_at, ...(source.staging_sha256 ? { staging_sha256: source.staging_sha256 } : {}) }));
  return { id: metric.id, category: metric.category, label: metric.label, description: metric.description, unit: metric.unit,
    aggregation: metric.aggregation, periods: metric.periods, latest_period: metric.latest_period, sources, has_monthly: metric.has_monthly };
}
async function cells(database: PoolClient, id: string, monthly = false, period?: string, code?: string | null): Promise<Cell[]> {
  const table = monthly ? 'values_monthly' : 'values_annual';
  const result = await database.query<Record<string, unknown>>(
    `SELECT code,period,value,status,weight FROM ${table} WHERE metric=$1 AND ($2::text IS NULL OR period=$2) AND ($3::text IS NULL OR code=$3) ORDER BY period`,
    [id, period ?? null, code ?? null],
  );
  return result.rows.map(row => ({
    code: String(row.code), period: String(row.period), value: row.value === null ? null : Number(row.value), status: String(row.status) as ValueStatus,
    weight: row.weight === null ? null : Number(row.weight),
  }));
}

/** Recompute ratios using same-source denominators; no mean of unweighted municipal rates. */
export function aggregate(rows: Cell[], method: AggregateMethod): { value: number | null; coverage: number } {
  const observed = rows.filter(row => row.status === 'observed' && row.value !== null && Number.isFinite(row.value)
    && (method !== 'weighted_mean' || row.weight !== null && row.weight > 0));
  if (!observed.length) return { value: null, coverage: 0 };
  const values = observed.map(row => row.value!);
  let value: number;
  if (method === 'weighted_mean') {
    value = observed.reduce((total, row) => total + row.value! * row.weight!, 0) / observed.reduce((total, row) => total + row.weight!, 0);
  } else if (method === 'median') {
    const ordered = [...values].sort((a,b) => a-b); const middle = Math.floor(ordered.length/2);
    value = ordered.length % 2 ? ordered[middle]! : (ordered[middle-1]!+ordered[middle]!)/2;
  } else {
    value = values.reduce((total, item) => total+item, 0) / (method === 'mean' ? values.length : 1);
  }
  return { value, coverage: new Set(observed.map(row => row.code)).size };
}

function current(metric: StoredMetric, rows: Cell[], code: string | null, name = 'Irpinia'): SectionCurrent {
  const selected = rows.filter(row => row.period === metric.latest_period && (!code || row.code === code));
  if (code) {
    const row = selected[0];
    return { period: metric.latest_period, value: row?.value ?? null, status: row?.status ?? 'unavailable', coverage: row?.status === 'observed' ? 1 : 0,
      scope: name, summary_label: 'Ultimo periodo disponibile della fonte' };
  }
  const result = aggregate(selected, metric.aggregation);
  const distinct = metric.regional_distinct?.[metric.latest_period];
  return { period: metric.latest_period, value: distinct ?? result.value, status: (distinct ?? result.value) === null ? 'unavailable' : 'observed',
    coverage: result.coverage, scope: 'Irpinia', summary_label: methodLabels[metric.aggregation] };
}

/** Keep a stable cohort for regional history; it can differ from latest-period coverage. */
function history(metric: StoredMetric, rows: Cell[], code: string | null, name: string, monthly = false): SectionHistory {
  const periods = [...new Set(rows.map(row => row.period))].sort();
  if (code) return { scope: name, label: metric.label, values: periods.map(period => {
    const row = rows.find(row => row.code === code && row.period === period);
    return { period, value: row?.value ?? null, status: row?.status ?? 'unavailable', coverage: row?.status === 'observed' ? 1 : 0 };
  }) };
  const byPeriod = periods.map(period => new Set(rows.filter(row => row.period === period && row.status === 'observed'
    && (metric.aggregation !== 'weighted_mean' || row.weight !== null && row.weight > 0)).map(row => row.code)));
  const cohort = byPeriod.length ? [...byPeriod[0]!].filter(code => byPeriod.every(set => set.has(code))) : [];
  const values: SectionPoint[] = periods.map(period => {
    const result = aggregate(rows.filter(row => row.period === period && cohort.includes(row.code)), metric.aggregation);
    const distinct = !monthly ? metric.regional_distinct?.[period] : undefined;
    return { period, value: distinct ?? result.value, status: (distinct ?? result.value) === null ? 'unavailable' : 'observed', coverage: result.coverage };
  });
  const scope = metric.aggregation === 'mean' ? `${cohort.length} punti meteo con dati in tutti i periodi` : `${cohort.length} comuni con dati in tutti i periodi`;
  return { scope: metric.aggregation === 'distinct' ? 'Elementi distinti nella raccolta' : scope, label: metric.label, values };
}

/** Retrieve a category's curated metrics and graphics from one validated publication. */
export async function section(database: PoolClient, categoryId: string, metricId?: string, code: string | null = null): Promise<SectionResponse> {
  const category = (await categories(database)).find(category => category.id === categoryId);
  if (!category) throw createError({ statusCode: 404, statusMessage: 'Unknown section' });
  const municipalities = await towns(database); const municipality = municipalities.find(town => town.code === code);
  if (code && !municipality) throw createError({ statusCode: 404, statusMessage: 'Unknown municipality' });
  const name = municipality?.name ?? 'Irpinia'; const definitions = await metrics(database, categoryId);
  const selected = definitions.find(metric => (!metric.presentation_role || metric.presentation_role==='public') && metric.id === (metricId ?? category.primary));
  if (!selected) throw createError({ statusCode: 404, statusMessage: 'Metric unavailable in this section' });
  const cache = new Map<string, Cell[]>();
  for (const metric of definitions) cache.set(metric.id, await cells(database, metric.id));
  const rows = cache.get(selected.id)!;
  const related = definitions.find(metric => metric.id === selected.recipe.related_history);
  const monthlyRows = selected.has_monthly ? (await cells(database, selected.id, true)).filter(row => row.period.startsWith(`${selected.latest_period}-`)) : [];
  return { category, municipalities, code, metric: publicMetric(selected),
    metrics: definitions.filter(metric => (!metric.presentation_role || metric.presentation_role==='public')).map(metric => ({ ...publicMetric(metric), current: current(metric, cache.get(metric.id)!, code, name) })),
    current: current(selected, rows, code, name), history: history(selected, rows, code, name),
    related_history: related ? history(related, cache.get(related.id)!, code, name) : null,
    monthly: monthlyRows.length ? history(selected, monthlyRows, code, name, true) : null,
    distribution: municipalities.map(town => {
      const row = rows.find(row => row.code === town.code && row.period === selected.latest_period);
      return { ...town, value: row?.value ?? null, status: row?.status ?? 'unavailable' };
    }),
  };
}

/** Summarize each section at the same selected scope without exposing full historical rows. */
export async function sectionOverview(database: PoolClient, code: string | null = null): Promise<SectionOverview> {
  const municipalities = await towns(database); const municipality = municipalities.find(town => town.code === code);
  if (code && !municipality) throw createError({ statusCode: 404, statusMessage: 'Unknown municipality' });
  const definitions = (await metrics(database)).filter(metric => (!metric.presentation_role || metric.presentation_role==='public'));
  const summaries: SectionSummaryMetric[] = [];
  for (const metric of definitions) {
    summaries.push({ ...publicMetric(metric), current: current(metric, await cells(database, metric.id, false, metric.latest_period, code), code, municipality?.name) });
  }
  const result = await database.query<Record<string, unknown>>('SELECT metadata::text AS metadata FROM publication');
  const publication = JSON.parse(String(result.rows[0]?.metadata)) as { generated_at: string };
  return { generated_at: publication.generated_at, metric_count: definitions.length, municipalities,
    categories: (await categories(database)).map(category => ({ ...category, metrics: summaries.filter(metric => metric.category === category.id) })) };
}

/** Read all chart-ready metrics in one consistent snapshot, without per-card requests. */
export async function territory(database: PoolClient, codes: string[]): Promise<TerritoryResponse> {
  const municipalities = await towns(database);
  const scopes = codes.length ? codes.map(code => {
    const town = municipalities.find(item => item.code === code);
    if (!town) throw createError({ statusCode: 404, statusMessage: 'Unknown municipality' });
    return town;
  }) : [{ code: null, name: 'Irpinia' }];
  const definitions = await metrics(database);
  const annual = await database.query<Cell & { metric: string }>('SELECT metric,code,period,value,status,weight FROM values_annual ORDER BY period');
  const monthly = await database.query<Cell & { metric: string }>('SELECT metric,code,period,value,status,weight FROM values_monthly ORDER BY period');
  const grouped = (rows: Array<Cell & { metric: string }>): Map<string, Cell[]> => {
    const result = new Map<string, Cell[]>();
    for (const row of rows) {
      const bucket = result.get(row.metric) ?? [];
      bucket.push(row); result.set(row.metric, bucket);
    }
    return result;
  };
  const annualByMetric = grouped(annual.rows); const monthlyByMetric = grouped(monthly.rows);
  const flows = await getDemographicFlows(database,scopes);
  const charts: TerritoryMetric[] = definitions.filter(metric => (!metric.presentation_role || metric.presentation_role==='public')).map(metric => {
    const rows = annualByMetric.get(metric.id) ?? [];
    const monthRows = (monthlyByMetric.get(metric.id) ?? []).filter(row => row.period.startsWith(`${metric.latest_period}-`));
    const latest = new Map(rows.filter(row => row.period === metric.latest_period).map(row => [row.code, row]));
    const related = metric.recipe.show_companion_history ? definitions.find(item => item.id===metric.recipe.related_history) : undefined;
    const flow = flows.get(metric.id);
    const breakdown = definitions.filter(item => item.presentation_role==='supporting_breakdown' && item.breakdown_parent===metric.id).map(item => {
      const companion = item.recipe.show_companion_history ? definitions.find(candidate => candidate.id===item.recipe.related_history) : undefined;
      return {metric:publicMetric(item),series:scopes.map(scope=>({...scope,current:current(item,annualByMetric.get(item.id) ?? [],scope.code,scope.name)})),
        ...(companion ? {historical:{metric:publicMetric(companion),series:scopes.map(scope=>({...scope,history:history(companion,annualByMetric.get(companion.id) ?? [],scope.code,scope.name)}))}} : {})};
    });
    return { ...publicMetric(metric), ...(flow ? {demographic_flow:flow} : {}), ...(breakdown.length ? {breakdown} : {}),
      ...(related ? {historical:{metric:publicMetric(related),series:scopes.map(scope=>({...scope,history:history(related,annualByMetric.get(related.id) ?? [],scope.code,scope.name)}))}} : {}),
      series: scopes.map(scope => ({ ...scope,
      current: current(metric, rows, scope.code, scope.name),
      history: history(metric, rows, scope.code, scope.name),
      monthly: monthRows.length ? history(metric, monthRows, scope.code, scope.name, true) : null,
    })), distribution: municipalities.map(town => {
      const row = latest.get(town.code);
      return { ...town, value: row?.value ?? null, status: row?.status ?? 'unavailable' };
    }) };
  });
  const publication = await database.query<{ metadata: { generated_at: string } }>('SELECT metadata FROM publication');
  return { generated_at: publication.rows[0]!.metadata.generated_at, municipalities, scopes,
    categories: (await categories(database)).map(category => ({ ...category, metrics: charts.filter(metric => metric.category === category.id) })) };
}
