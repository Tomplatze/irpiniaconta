import type { PoolClient } from 'pg';
import type { Dataset, Indicator, Municipality, Overview } from '../../shared/types';

/** Load catalogue order and measured coverage without a query for every indicator. */
export async function readCatalog(database: PoolClient): Promise<Dataset[]> {
  const datasets = await database.query<Record<string, unknown>>('SELECT metadata::text AS metadata, verified_at FROM datasets ORDER BY position');
  const indicators = await database.query<Record<string, unknown>>('SELECT id,dataset_id,label,unit,definition FROM indicators ORDER BY position');
  const coverage = await database.query<Record<string, unknown>>('SELECT indicator_id,period,status,COUNT(*) AS count FROM observations GROUP BY indicator_id,period,status ORDER BY period DESC');
  const total = await database.query<Record<string, unknown>>('SELECT COUNT(*) AS count FROM municipalities');
  const municipalityCount = Number(total.rows[0]?.count ?? 0);
  return datasets.rows.map(row => {
    const metadata = JSON.parse(String(row.metadata)) as Omit<Dataset, 'indicators'>;
    return { ...metadata, verified_at: String(row.verified_at), indicators: indicators.rows.filter(indicator => indicator.dataset_id === metadata.id).map(indicator => {
      const counts = coverage.rows.filter(item => item.indicator_id === indicator.id);
      const periods = [...new Set(counts.map(item => String(item.period)))];
      const latest = periods[0] ?? null;
      const latestCounts = counts.filter(item => item.period === latest);
      const count = (status: string): number => Number(latestCounts.find(item => item.status === status)?.count ?? 0);
      return { id: String(indicator.id), dataset_id: metadata.id, label: String(indicator.label), unit: String(indicator.unit),
        definition: String(indicator.definition), periods, latest_period: latest,
        observed_count: count('observed'), suppressed_count: count('suppressed'), missing_count: count('missing'),
        absent_count: municipalityCount - latestCounts.reduce((sum, item) => sum + Number(item.count), 0) } satisfies Indicator;
    }) };
  });
}

/** Read the canonical ISTAT registry without matching by municipality names. */
export async function readMunicipalities(database: PoolClient): Promise<Municipality[]> {
  const result = await database.query<Record<string, unknown>>('SELECT code,name,province_code,region_code FROM municipalities ORDER BY lower(name),name,code');
  return result.rows.map(row => ({ code: String(row.code), name: String(row.name), province_code: String(row.province_code), region_code: String(row.region_code) }));
}

/** Return measured source readiness separately from the registered municipality count. */
export async function readOverview(database: PoolClient): Promise<Overview> {
  const datasets = await readCatalog(database);
  const municipalities = await readMunicipalities(database);
  const runs = await database.query<Record<string, unknown>>('SELECT completed_at,mode FROM ingestion_runs ORDER BY completed_at DESC LIMIT 1');
  const observations = await database.query<Record<string, unknown>>('SELECT COUNT(*) AS count FROM observations WHERE status=$1', ['observed']);
  const run = runs.rows[0];
  return { municipalities, datasets, summary: {
    municipality_count: municipalities.length, ready_sources: datasets.filter(dataset => dataset.status === 'ready').length,
    total_sources: datasets.length, observation_count: Number(observations.rows[0]?.count ?? 0),
    last_run: String(run?.completed_at ?? ''), mode: String(run?.mode ?? ''),
    acquired_at: datasets.flatMap(dataset => dataset.artifacts.map(artifact => artifact.retrieved_at)).sort().at(-1) ?? '',
  } };
}
