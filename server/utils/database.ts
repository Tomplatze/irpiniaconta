import { Pool, type PoolClient } from 'pg';

let pool: Pool | undefined;

/** Reuse a bounded server-only pool; connection details never enter public responses. */
function connectionPool(): Pool {
  if (pool) return pool;
  const connectionString = Reflect.get(process.env, 'DATABASE_READ_URL') ?? useRuntimeConfig().databaseReadUrl;
  if (typeof connectionString !== 'string' || !connectionString) {
    throw createError({ statusCode: 503, statusMessage: 'Database unavailable. Run npm run db:reader to configure API read access.' });
  }
  pool = new Pool({ connectionString, max: 5, connectionTimeoutMillis: 5000,
    idleTimeoutMillis: 10000, statement_timeout: 10000, query_timeout: 10000,
    application_name: 'atlante-irpinia', allowExitOnIdle: true });
  pool.on('error', () => console.error('An idle database connection failed.'));
  return pool;
}

/** Release the pool when Nitro shuts down, including development reloads. */
export async function closeDatabase(): Promise<void> {
  const active = pool;
  pool = undefined;
  await active?.end();
}

/** Read a consistent publication; an ETL commit becomes visible on the next request. */
export async function withDatabase<T>(read: (database: PoolClient) => Promise<T>, schema: 'atlas' | 'sections' = 'atlas'): Promise<T> {
  let database: PoolClient | undefined;
  let discardConnection = false;
  try {
    database = await connectionPool().connect();
    await database.query('BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY');
    await database.query(schema === 'sections'
      ? 'SET LOCAL search_path TO sections, public, pg_catalog'
      : 'SET LOCAL search_path TO atlas, public, pg_catalog');
    const result = await read(database);
    await database.query('COMMIT');
    return result;
  } catch (error) {
    if (database) await database.query('ROLLBACK').catch(() => { discardConnection = true; });
    if (error !== null && typeof error === 'object' && 'statusCode' in error && typeof error.statusCode === 'number') throw error;
    discardConnection = true;
    throw createError({ statusCode: 503, statusMessage: 'Database unavailable. Verify the local PostgreSQL service and migrations.' });
  } finally {
    database?.release(discardConnection);
  }
}
