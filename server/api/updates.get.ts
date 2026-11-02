import type { RunSummary } from '../../shared/catalogue';
import { withDatabase } from '../utils/database';

/** Keep internal ingestion history unavailable in production builds. */
export default defineEventHandler(() => {
  if (!import.meta.dev) throw createError({ statusCode: 404, statusMessage: 'Not Found' });
  return withDatabase(async database => {
  const result = await database.query<Record<string, unknown>>('SELECT id,completed_at,mode,report::text AS report FROM ingestion_runs ORDER BY completed_at DESC LIMIT 20');
  return result.rows.map((row): RunSummary => {
    const report = JSON.parse(String(row.report)) as { attempts?: Array<{ status: string }>; quality: Array<{ status: string }> };
    return { id: String(row.id), completed_at: String(row.completed_at), mode: String(row.mode),
      attempted: report.attempts?.length ?? 0, failed: report.attempts?.filter(attempt => attempt.status === 'blocked').length ?? 0,
      ready: report.quality.filter(source => source.status === 'ready').length };
  });
  });
});
