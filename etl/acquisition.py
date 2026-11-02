"""Acquire or replay immutable source bytes independently of database publication."""
from pathlib import Path
from typing import Literal
import hashlib
import json
import urllib.request
import urllib.error
import ssl
import subprocess
import tempfile
from datetime import datetime, timezone

class Context:
    """Download immutable source artifacts with reproducible acquisition evidence."""
    def __init__(self, raw_dir: Path, offline: bool = False):
        self.raw_dir = raw_dir
        self.offline = offline
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts: list[dict[str, object]] = []

    def fetch(self, url: str, filename: str, *, method: Literal['GET', 'POST'] = 'GET', body: object | None = None) -> Path:
        """Fetch or explicitly replay an artifact; never treat HTML as data."""
        path = self.raw_dir / filename
        proof = path.with_suffix(path.suffix + '.acquisition.json')
        if self.offline:
            if not path.exists() or not proof.exists():
                raise RuntimeError(f'Offline artifact not available: {filename}')
            record = json.loads(proof.read_text())
            if record.get('url') != url or record.get('filename') != filename or record.get('method', 'GET') != method:
                raise RuntimeError(f'Artifact request provenance mismatch: {filename}')
            if body != record.get('request_body'):
                raise RuntimeError(f'Artifact request body mismatch: {filename}')
            if body is not None and record.get('request_sha256') != hashlib.sha256(json.dumps(record['request_body']).encode('utf-8')).hexdigest():
                raise RuntimeError(f'Artifact request checksum mismatch: {filename}')
            digest = hashlib.sha256()
            with path.open('rb') as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b''):
                    digest.update(chunk)
            if record['sha256'] != digest.hexdigest() or record.get('bytes') != path.stat().st_size:
                raise RuntimeError(f'Artifact checksum mismatch: {filename}')
            self.artifacts.append(record)
            return path
        request_payload = json.dumps(body).encode('utf-8') if body is not None else None
        headers = {'User-Agent': 'AtlanteIrpiniaPrototype/0.1 (institutional data verification)', 'Accept-Language': 'it'}
        if request_payload is not None:
            headers['Content-Type'] = 'application/json'
        request = urllib.request.Request(url, data=request_payload, method=method, headers=headers)
        try:
            response = urllib.request.urlopen(request, timeout=40)
        except urllib.error.URLError as error:
            if method != 'GET' or not isinstance(error.reason, ssl.SSLError):
                raise
            return self.fetch_with_curl(url, filename, str(error.reason))
        with response:
            payload = response.read()
            record = {'url': url, 'resolved_url': response.url, 'http_status': response.status,
                      'content_type': response.headers.get('Content-Type'), 'bytes': len(payload),
                      'sha256': hashlib.sha256(payload).hexdigest(),
                      'retrieved_at': datetime.now(timezone.utc).isoformat(), 'filename': filename, 'method': method}
            if body is not None:
                record['request_body'] = body
                record['request_sha256'] = hashlib.sha256(request_payload).hexdigest()
        archive = self.raw_dir / 'archive' / record['sha256']
        archive.parent.mkdir(exist_ok=True)
        if not archive.exists():
            archive.write_bytes(payload)
        record['archive_path'] = str(archive.relative_to(self.raw_dir.parent))
        path.write_bytes(payload)
        proof.write_text(json.dumps(record, indent=2) + '\n')
        self.artifacts.append(record)
        return path

    def fetch_with_curl(self, url: str, filename: str, fallback_reason: str) -> Path:
        """Use the OS HTTPS client only for TLS interoperability failures; certificate checks stay enabled."""
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory) / 'response'
            process = subprocess.run(['curl', '--silent', '--show-error', '--fail', '--location',
                '--proto', '=https', '--proto-redir', '=https', '--max-time', '40',
                '--output', str(temporary), '--write-out', '%{json}', url], capture_output=True, text=True, check=True)
            details = json.loads(process.stdout)
            if details['http_code'] != 200: raise RuntimeError('Unexpected curl HTTP response status')
            payload = temporary.read_bytes()
        path = self.raw_dir / filename
        record = {'url': url, 'resolved_url': details['url_effective'], 'http_status': details['http_code'],
                  'content_type': details['content_type'], 'bytes': len(payload),
                  'sha256': hashlib.sha256(payload).hexdigest(), 'retrieved_at': datetime.now(timezone.utc).isoformat(),
                  'filename': filename, 'method': 'GET', 'transport': 'curl', 'fallback_reason': fallback_reason}
        archive = self.raw_dir / 'archive' / record['sha256']
        archive.parent.mkdir(exist_ok=True)
        if not archive.exists(): archive.write_bytes(payload)
        record['archive_path'] = str(archive.relative_to(self.raw_dir.parent))
        path.write_bytes(payload)
        path.with_suffix(path.suffix + '.acquisition.json').write_text(json.dumps(record, indent=2) + '\n')
        self.artifacts.append(record)
        return path
