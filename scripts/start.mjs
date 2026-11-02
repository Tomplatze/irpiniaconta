// Database setup and imports are explicit operations, independent of application startup.
process.env.HOST ||= '127.0.0.1';
await import('../.output/server/index.mjs');
