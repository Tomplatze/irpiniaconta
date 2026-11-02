import type { PoolClient } from 'pg';
import type { Dataset, Indicator, Municipality, ValueStatus } from '../../shared/types';
import type { Exploration, Series } from '../../shared/catalogue';
import { readCatalog, readMunicipalities } from './catalog';

/** Look up a metric only through the declared source catalogue. */
export async function findIndicator(database: PoolClient, id: string): Promise<{ indicator: Indicator; dataset: Dataset }> {
  for (const dataset of await readCatalog(database)) {
    const indicator = dataset.indicators.find(item => item.id === id);
    if (indicator) return { indicator, dataset };
  }
  throw createError({ statusCode: 404, statusMessage: 'Unknown indicator' });
}

/** Use one explicit period; absence remains unavailable instead of becoming zero. */
export async function explore(database: PoolClient, id: string, selectedPeriod?: string): Promise<Exploration> {
  const { indicator } = await findIndicator(database, id);
  const period = selectedPeriod ?? indicator.latest_period;
  if (!period || !indicator.periods.includes(period)) throw createError({ statusCode: 404, statusMessage: 'Unavailable period' });
  const cells = await database.query<Record<string, unknown>>('SELECT municipality_code,value,status FROM observations WHERE indicator_id=$1 AND period=$2', [id, period]);
  const municipalities = await readMunicipalities(database);
  const byCode = new Map(cells.rows.map(row => [String(row.municipality_code), row]));
  return { indicator, period, values: municipalities.map(municipality => {
    const cell = byCode.get(municipality.code);
    return { ...municipality, value: cell?.value === null || cell?.value === undefined ? null : Number(cell.value),
      status: cell ? String(cell.status) as ValueStatus : 'unavailable' };
  }) };
}

/** Retrieve all published periods, including missing observations, for exact municipal codes. */
export async function series(database: PoolClient, id: string, codes: string[]): Promise<Series> {
  const { indicator, dataset } = await findIndicator(database, id);
  const registry = await readMunicipalities(database);
  const municipalities = codes.map((code): Municipality => {
    const municipality = registry.find(row => row.code === code);
    if (!municipality) throw createError({ statusCode: 404, statusMessage: 'Unknown municipality' });
    return municipality;
  });
  const result = await database.query<Record<string, unknown>>('SELECT municipality_code,period,value,status FROM observations WHERE indicator_id=$1 AND municipality_code=ANY($2::text[])', [id, codes]);
  const cells = new Map(result.rows.map(row => [`${row.municipality_code}:${row.period}`, row]));
  return { indicator, dataset, municipalities: municipalities.map(municipality => ({ ...municipality,
    values: [...indicator.periods].sort().map(period => {
      const cell = cells.get(`${municipality.code}:${period}`);
      return { period, value: cell?.value === null || cell?.value === undefined ? null : Number(cell.value), status: cell ? String(cell.status) as ValueStatus : 'unavailable' };
    }),
  })) };
}
