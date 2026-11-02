import { spawnSync } from 'node:child_process';

// Derive Docker settings from the same URL used by Python and Nitro.
let connection;
try { connection = new URL(process.env.DATABASE_URL ?? ''); }
catch { throw new Error('Set a local PostgreSQL DATABASE_URL in .env before running db commands.'); }
if (!['postgres:', 'postgresql:'].includes(connection.protocol)
  || !['127.0.0.1', 'localhost'].includes(connection.hostname)
  || !connection.username || !connection.password || connection.pathname === '/') {
  throw new Error('db commands require a complete local PostgreSQL DATABASE_URL in .env.');
}
const commands = { up: ['up', '-d', '--wait', 'postgres'], down: ['stop', 'postgres'], restart: ['restart', 'postgres'], status: ['ps', 'postgres'] };
const command = commands[process.argv[2]];
if (!command) throw new Error('Expected db command: up, down, restart or status.');
const result = spawnSync('docker', ['compose', ...command], {
  stdio: 'inherit',
  env: { ...process.env, POSTGRES_DB: decodeURIComponent(connection.pathname.slice(1)),
    POSTGRES_USER: decodeURIComponent(connection.username), POSTGRES_PASSWORD: decodeURIComponent(connection.password),
    POSTGRES_PORT: connection.port || '5432' },
});
process.exit(result.status ?? 1);
