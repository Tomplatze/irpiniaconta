import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';

const maxFileBytes = 2 * 1024 * 1024;
const maxTotalBytes = 10 * 1024 * 1024;
const generatedPath = /(^|\/)(node_modules|\.nuxt|\.output|\.venv(?:-[^/]*)?|venv|__pycache__|\.cache|\.data|dist|coverage|work|\.local|\.idea|\.vscode)(\/|$)/;
const privateFile = /(^|\/)(?:\.env(?:\..+)?|[^/]+\.(?:pem|key|p12|pfx|sqlite(?:3)?(?:-.*)?|dump|backup|log|py[cod]|tsbuildinfo)|\.DS_Store|\._[^/]+)$/;
const generatedEvidence = /^docs\/(?:screenshots\/|[^/]+-preview\.png$|[^/]+\.json$|evidence\/npm-audit-[^/]+\.json$)/;
const secretPatterns = [
  /-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----/,
  /\bgh[pousr]_[A-Za-z0-9]{36,}\b/,
  /\bgithub_pat_[A-Za-z0-9_]{50,}\b/,
  /\bAKIA[A-Z0-9]{16}\b/,
  /\bsk-(?:proj-)?[A-Za-z0-9_-]{40,}\b/,
  /\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?):\/\/[^\s/:]+:([^\s@]+)@/g,
];

/** Check tracked content as staged, plus untracked candidates allowed by Git. */
function checkRepository() {
  const tracked = new Set(execFileSync('git', ['ls-files', '--cached', '-z'], { encoding: 'utf8' }).split('\0').filter(Boolean));
  const candidates = new Set(execFileSync('git', ['ls-files', '--cached', '--others', '--exclude-standard', '-z'], { encoding: 'utf8' }).split('\0').filter(Boolean));
  const issues = [];
  let totalBytes = 0;
  for (const path of candidates) {
    if (generatedPath.test(path) || (privateFile.test(path) && path !== '.env.example')
      || (path.startsWith('data/') && path !== 'data/README.md') || generatedEvidence.test(path)) {
      issues.push(`${path}: private or generated file must stay outside Git`);
      continue;
    }
    const payload = tracked.has(path)
      ? execFileSync('git', ['show', `:${path}`], { maxBuffer: 20 * 1024 * 1024 })
      : readFileSync(path);
    totalBytes += payload.length;
    if (payload.length > maxFileBytes) issues.push(`${path}: exceeds the 2 MiB per-file budget`);
    if (payload.includes(0)) continue;
    const content = payload.toString('utf8');
    for (const pattern of secretPatterns) {
      pattern.lastIndex = 0;
      for (const match of content.matchAll(new RegExp(pattern.source, 'g'))) {
        if (match[1] && ['change-me', 'password', '<password>'].includes(match[1]) && path === '.env.example') continue;
        issues.push(`${path}: possible credential; review locally (value withheld)`);
        break;
      }
    }
  }
  if (totalBytes > maxTotalBytes) issues.push('Repository candidates exceed the 10 MiB total budget');
  if (issues.length) {
    console.error(issues.join('\n'));
    process.exitCode = 1;
    return;
  }
  console.log(`Repository check passed: ${candidates.size} files, ${(totalBytes / 1024 / 1024).toFixed(2)} MiB. No generated data or recognized credential patterns found.`);
}

checkRepository();
