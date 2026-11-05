import { snapshotComparison } from '../utils/snapshot-legacy';
import { useSnapshotPublication } from '../utils/snapshot';
import type { Comparison, ComparisonRow } from '../../shared/types';
import { withDatabase } from '../utils/database';
import { readCatalog, readMunicipalities } from '../utils/catalog';

/** Compare two to four municipalities using one explicit common period per indicator. */
export default defineEventHandler((event): Promise<Comparison> => {
  const query = getQuery(event);
  if (typeof query.codes !== 'string') throw createError({ statusCode: 400, statusMessage: 'codes is required' });
  const codes = query.codes.split(',');
  if (codes.length < 2 || codes.length > 4 || new Set(codes).size !== codes.length || codes.some(code => !/^064\d{3}$/.test(code))) {
    throw createError({ statusCode: 400, statusMessage: 'Provide two to four distinct six-digit Avellino ISTAT codes' });
  }
  if (query.indicator !== undefined && typeof query.indicator !== 'string') throw createError({ statusCode: 400, statusMessage: 'Invalid indicator' });
  if (query.period !== undefined && (typeof query.period !== 'string' || !/^\d{4}(?:-\d{2}-\d{2})?$/.test(query.period) || !query.indicator)) {
    throw createError({ statusCode: 400, statusMessage: 'An explicit period requires a valid indicator' });
  }
  if (useSnapshotPublication()) return snapshotComparison(codes,query.indicator as string | undefined,query.period as string | undefined);
  return withDatabase(async database => {
    const registry = await readMunicipalities(database);
    const datasets = await readCatalog(database);
    const municipalities = codes.map(code => {
      const municipality = registry.find(item => item.code === code);
      if (!municipality) throw createError({ statusCode: 404, statusMessage: 'Municipality not in the current ISTAT registry' });
      return municipality;
    });
    const indicators = datasets.flatMap(dataset => dataset.indicators);
    if (query.indicator && !indicators.some(indicator => indicator.id === query.indicator)) {
      throw createError({ statusCode: 404, statusMessage: 'Unknown indicator' });
    }
    const result = await database.query<Record<string, unknown>>('SELECT municipality_code,indicator_id,period,value,status FROM observations WHERE municipality_code=ANY($1::text[])', [codes]);
    const cells = new Map(result.rows.map(row => [`${row.municipality_code}:${row.indicator_id}:${row.period}`, row]));
    const rows: ComparisonRow[] = indicators.filter(indicator => !query.indicator || indicator.id === query.indicator).map(indicator => {
      const period = typeof query.period === 'string' ? query.period : indicator.latest_period;
      if (query.period && !indicator.periods.includes(query.period as string)) {
        throw createError({ statusCode: 404, statusMessage: 'Period unavailable for this indicator' });
      }
      return { indicator, dataset_id: indicator.dataset_id, period, measurements: municipalities.map(municipality => {
        const record = cells.get(`${municipality.code}:${indicator.id}:${period}`);
        return { code: municipality.code, name: municipality.name, value: record?.value === null || record?.value === undefined ? null : Number(record.value),
          status: record ? String(record.status) as 'observed' | 'missing' | 'suppressed' : 'unavailable' };
      }) };
    });
    return { municipalities, rows };
  });
});
