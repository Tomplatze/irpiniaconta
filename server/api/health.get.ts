import { withDatabase } from '../utils/database';

/** Check PostgreSQL connectivity, validated constraints and canonical registry coverage. */
export default defineEventHandler(() => withDatabase(async database => {
  const coverage = await database.query<Record<string, unknown>>('SELECT (SELECT COUNT(*) FROM municipalities) AS count,(SELECT COUNT(*) FROM sections.municipalities) AS sections_count');
  const constraints = await database.query<Record<string, unknown>>("SELECT COUNT(*) AS count FROM pg_constraint c JOIN pg_namespace n ON n.oid=c.connamespace WHERE n.nspname IN ('atlas','sections') AND NOT c.convalidated");
  const municipalities = Number(coverage.rows[0]?.count ?? 0);
  if (municipalities !== 118 || Number(coverage.rows[0]?.sections_count ?? 0) !== 118 || Number(constraints.rows[0]?.count ?? 0) !== 0) {
    throw createError({ statusCode: 503, statusMessage: 'Database publication validation failed.' });
  }
  return { status: 'ok', integrity: 'ok', municipalities };
}));
