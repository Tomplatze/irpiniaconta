"""Collect unchanged, source-labelled municipal emblems from the public AV catalogue."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
import argparse
import hashlib
import json
import re
import time
import unicodedata

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / 'data' / 'municipal-crests'
CATALOGUE = ('https://www.araldicacivica.it/comuni/?wpv_view_count=160984'
             '&wpv_post_search=&wpv-wpcf-sigla-provincia-comune=AV'
             '&wpv-wpcf-prefisso-telefonico-comune=&wpv-wpcf-cap-comune=&wpv_filter_submit=Vai')
HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; IrpiniaConta/0.9; +https://irpiniaconta.it)'}
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


def fetch(url: str) -> bytes:
    """Fetch one public source URL, allowing temporary publisher errors to recover."""
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers=HEADERS), timeout=35) as response:
                return response.read()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))
    raise RuntimeError('Unreachable')


def normalized(value: str) -> str:
    """Normalize typography only; never infer an association from partial names."""
    return ' '.join(unicodedata.normalize('NFKC', value).casefold().replace('’', "'").split())


class Node:
    """Minimal HTML tree used to retain the heading and image relationship."""
    def __init__(self, tag: str, attrs: dict[str, str], parent: Node | None):
        self.tag, self.attrs, self.parent = tag, attrs, parent
        self.children: list[Node | str] = []

    def text(self) -> str:
        return ''.join(child if isinstance(child, str) else child.text() for child in self.children)

    def elements(self):
        for child in self.children:
            if isinstance(child, Node):
                yield child
                yield from child.elements()


class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node('root', {}, None)
        self.current = self.root

    def handle_starttag(self, tag, attrs):
        node = Node(tag, dict(attrs), self.current)
        self.current.children.append(node)
        if tag not in VOID:
            self.current = node

    def handle_startendtag(self, tag, attrs):
        self.current.children.append(Node(tag, dict(attrs), self.current))

    def handle_endtag(self, tag):
        node = self.current
        while node.parent is not None:
            if node.tag == tag:
                self.current = node.parent
                return
            node = node.parent

    def handle_data(self, data):
        self.current.children.append(data)


def parse(data: bytes) -> Node:
    parser = Document()
    parser.feed(data.decode('utf-8', errors='replace'))
    return parser.root


def catalogue() -> list[tuple[str, str]]:
    """Follow publisher pagination and retain only named municipal result links."""
    address = CATALOGUE
    visited: set[str] = set()
    records = []
    while address and address not in visited:
        visited.add(address)
        doc = parse(fetch(address))
        for node in doc.elements():
            if node.tag == 'h3':
                for link in node.elements():
                    href = link.attrs.get('href', '')
                    if link.tag == 'a' and '/comune/' in href:
                        records.append((link.text().strip(), urljoin(address, href)))
        following = [urljoin(address, n.attrs.get('href', '')) for n in doc.elements()
                     if n.tag == 'a' and n.text().strip() == 'Seguente' and n.attrs.get('href')]
        address = following[0] if following else ''
        print(f'Catalogue: {len(visited)} pages, {len(records)} records', flush=True)
        time.sleep(.3)
    return records


def municipal_images(record: tuple[str, str, str]) -> dict:
    """Prefer the official image; retain a labelled redrawing as a fallback."""
    code, name, page = record
    try:
        doc = parse(fetch(page))
        headings = [re.match(r'^\s*(?:Comune|Città)\s+di\s+(.+?)\s*[–—-]\s*\(AV\)\s*$', n.text(), re.IGNORECASE)
                    for n in doc.elements() if n.tag == 'h2']
        if not any(match and normalized(match.group(1)) == normalized(name) for match in headings):
            return {'code': code, 'name': name, 'page': page, 'error': 'Municipal heading not verified'}
        candidates = []
        for label, kind in [('stemma ufficiale', 'official'), ('stemma ridisegnato', 'redrawn')]:
            for node in doc.elements():
                if node.tag not in {'h3', 'h4', 'h5', 'h6'} or normalized(node.text()) != label or not node.parent:
                    continue
                images = [n.attrs.get('src', '') for n in node.parent.elements() if n.tag == 'img' and n.attrs.get('src')]
                if images:
                    image = urljoin(page, images[0])
                    if urlparse(image).hostname not in {'www.araldicacivica.it', 'araldicacivica.it'}:
                        continue
                    if re.search(r'(?:^|/)no[-_]stemma\.', urlparse(image).path, re.IGNORECASE):
                        continue
                    info = node.parent.text().partition('Fonte:')[2].strip()
                    candidates.append({'image': image, 'kind': kind, **({'artist': info} if info else {})})
                    break
        return {'code': code, 'name': name, 'page': page, 'candidates': candidates}
    except Exception as error:
        return {'code': code, 'name': name, 'page': page, 'error': str(error)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--resume', action='store_true', help='Retry incomplete records in the existing manifest')
    args = parser.parse_args()
    registry = json.loads((ROOT / 'data/snapshot.json').read_text())['municipalities']
    names = {normalized(item['name']): item for item in registry}
    manifest_path = OUTPUT / 'manifest.json'
    previous = json.loads(manifest_path.read_text())['records'] if args.resume and manifest_path.exists() else []
    if previous:
        expected = {item['code']: item['name'] for item in registry}
        if len(previous) != len(expected) or any(expected.get(row['code']) != row['name'] for row in previous):
            raise ValueError('Existing manifest does not match the municipal registry')
        retained = [row for row in previous if row.get('file') and not re.search(r'(?:^|/)no[-_]stemma\.', urlparse(row.get('image', '')).path, re.IGNORECASE)]
        pending = [row for row in previous if row not in retained]
        for row in pending:
            if row.get('filename') and re.fullmatch(r'064\d{3}\.(?:jpg|png|gif|webp)', row['filename']):
                (OUTPUT / row['filename']).unlink(missing_ok=True)
        matches = [(row['code'], row['name'], row['page']) for row in pending if row.get('page')]
        missing = [row for row in pending if not row.get('page')]
        print(f'Retained {len(retained)} valid images; checking {len(matches)} remaining pages', flush=True)
    else:
        retained = []
        candidates: dict[str, list[str]] = {}
        for name, page in catalogue():
            candidates.setdefault(normalized(name), []).append(page)
        matches = []
        missing = []
        for key, municipality in names.items():
            links = list(dict.fromkeys(candidates.get(key, [])))
            if len(links) == 1:
                matches.append((municipality['code'], municipality['name'], links[0]))
            else:
                missing.append({'code': municipality['code'], 'name': municipality['name'], 'error': f'{len(links)} exact catalogue matches'})
    print(f'Exact matches: {len(matches)}/{len(registry)}', flush=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = []
        for index, result in enumerate(pool.map(municipal_images, matches), 1):
            results.append(result)
            if index % 10 == 0 or index == len(matches):
                print(f'Checked municipal pages: {index}/{len(matches)}', flush=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    def acquire(record):
        errors = []
        for candidate in record.pop('candidates', []):
            try:
                payload = fetch(candidate['image'])
                if payload.startswith(b'\xff\xd8\xff'):
                    suffix = '.jpg'
                elif payload.startswith(b'\x89PNG\r\n\x1a\n'):
                    suffix = '.png'
                elif payload.startswith((b'GIF87a', b'GIF89a')):
                    suffix = '.gif'
                elif payload[:4] == b'RIFF' and payload[8:12] == b'WEBP':
                    suffix = '.webp'
                else:
                    raise ValueError('Image format not verified')
                filename = record['code'] + suffix
                (OUTPUT / filename).write_bytes(payload)
                record.update(candidate)
                record['filename'] = filename
                record['sha256'] = hashlib.sha256(payload).hexdigest()
                record['file'] = '/api/municipal-crests/' + record['code']
                return record
            except Exception as error:
                errors.append(str(error))
        if not record.get('error'):
            record['error'] = 'No image acquired' + (': ' + '; '.join(errors) if errors else '')
        return record
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(acquire, results))
    records = sorted(retained + results + missing, key=lambda row: row['code'])
    manifest = {'source': 'https://www.araldicacivica.it/comuni/', 'license': 'CC BY-NC-ND 3.0',
                'license_url': 'https://creativecommons.org/licenses/by-nc-nd/3.0/',
                'rights_note': 'Publisher terms describe non-commercial use with attribution and no derivatives. Official emblems can be subject to institutional rights.',
                'records': records}
    (OUTPUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(f"Acquired {sum('file' in r for r in records)}/{len(registry)} official images or labelled redrawings", flush=True)
    for record in records:
        if record.get('error'):
            print(record['code'], record['name'], record['error'], flush=True)


if __name__ == '__main__':
    main()
