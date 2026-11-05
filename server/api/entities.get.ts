import { snapshotEntities } from '../utils/snapshot-legacy';
import { useSnapshotPublication } from '../utils/snapshot';
import type { EntityPage } from '../../shared/catalogue';
import { withDatabase } from '../utils/database';
import { entityRecord, readScope } from '../utils/scope';

/** Browse source records with bounded pagination and exact municipal associations. */
export default defineEventHandler((event): Promise<EntityPage> => {
  const query = getQuery(event);
  const offset = query.offset === undefined ? 0 : Number(query.offset);
  const limit = query.limit === undefined ? 30 : Number(query.limit);
  if (!Number.isInteger(offset) || offset < 0 || !Number.isInteger(limit) || limit < 1 || limit > 100) throw createError({ statusCode: 400, statusMessage: 'Invalid pagination' });
  if (query.code !== undefined && (typeof query.code !== 'string' || !/^064\d{3}$/.test(query.code))) throw createError({ statusCode: 400, statusMessage: 'Invalid municipal code' });
  if (query.category !== undefined && typeof query.category !== 'string') throw createError({ statusCode: 400, statusMessage: 'Invalid category' });
  if (useSnapshotPublication()) return snapshotEntities(offset,limit,query.code as string | undefined,query.category as string | undefined);
  return withDatabase(async database => {
    const scope = await readScope(database);
    if (query.category && !scope.categories.some(category => category.id === query.category)) throw createError({ statusCode: 404, statusMessage: 'Unknown category' });
    if (query.code && !(await database.query<Record<string, unknown>>('SELECT code FROM municipalities WHERE code=$1', [query.code])).rowCount) throw createError({ statusCode: 404, statusMessage: 'Unknown municipality' });
    const ids = scope.sources.filter(source => !query.category || source.category_id === query.category).map(source => source.dataset?.id).filter((id): id is string => typeof id === 'string');
    if (!ids.length) return { total: 0, records: [], limit, offset };
    const parameters: Array<string | string[] | number> = [ids];
    let where = 'e.dataset_id=ANY($1::text[])';
    if (typeof query.code === 'string') { parameters.push(query.code); where += ` AND e.municipality_code=$${parameters.length}`; }
    const totalResult = await database.query<Record<string, unknown>>(`SELECT COUNT(*) AS total FROM entities e WHERE ${where}`, parameters);
    const total = Number(totalResult.rows[0]?.total ?? 0);
    parameters.push(limit, offset);
    const result = await database.query<Record<string, unknown>>(`SELECT e.dataset_id,e.source_id,e.municipality_code,e.title,e.kind,e.period,e.payload::text AS payload,m.name AS municipality_name
      FROM entities e LEFT JOIN municipalities m ON m.code=e.municipality_code WHERE ${where}
      ORDER BY lower(e.title),e.title,e.source_id LIMIT $${parameters.length - 1} OFFSET $${parameters.length}`, parameters);
    return { total, records: result.rows.map(entityRecord), limit, offset };
  });
});
