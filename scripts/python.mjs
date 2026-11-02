import { existsSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { resolve } from 'node:path';

const interpreter = process.env.PYTHON_BIN || (existsSync('.venv/bin/python') ? resolve('.venv/bin/python') : 'python3');
const result = spawnSync(interpreter, ['-m', ...process.argv.slice(2)], { stdio: 'inherit' });
process.exit(result.status ?? 1);
