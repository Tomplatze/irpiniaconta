"""Provision a dedicated local API login with SELECT privileges only."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import secrets
from urllib.parse import quote, unquote, urlsplit

import psycopg
from psycopg import sql

from etl.database import connect, require_current_schema
from etl.settings import environment_value

ROOT = Path(__file__).resolve().parents[1]


def provision(root: Path = ROOT) -> str:
    """Grant a separate login access to publication schemas without granting write capabilities."""
    writer = environment_value('DATABASE_URL', root)
    if not writer:
        raise ValueError('Configure DATABASE_URL before provisioning the API reader')
    writer_url = urlsplit(writer)
    if writer_url.hostname not in {'localhost', '127.0.0.1'}:
        raise ValueError('Automatic reader provisioning is limited to the local PostgreSQL service')
    existing = environment_value('DATABASE_READ_URL', root)
    identity = 'atlas_reader_' + hashlib.sha256(writer_url.path.encode()).hexdigest()[:12]
    password = secrets.token_urlsafe(32)
    if existing:
        reader_url = urlsplit(existing)
        if (reader_url.hostname != writer_url.hostname or reader_url.port != writer_url.port
                or reader_url.path != writer_url.path or reader_url.username == writer_url.username
                or reader_url.scheme not in {'postgres', 'postgresql'}
                or not reader_url.username or not reader_url.password):
            raise ValueError('DATABASE_READ_URL must identify a distinct login on the same local database')
        identity = unquote(reader_url.username)
        password = unquote(reader_url.password)
    url = writer_url._replace(netloc=f'{quote(identity, safe="")}:{quote(password, safe="")}@'
                             f'{writer_url.hostname}:{writer_url.port or 5432}', query='', fragment='').geturl()
    with connect(writer) as database, database.transaction():
        require_current_schema(database)
        flags = database.execute('''SELECT rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls
            FROM pg_roles WHERE rolname=%s''', (identity,)).fetchone()
        if flags and any(flags):
            raise ValueError('Refusing to reuse a privileged PostgreSQL role as the API reader')
        if flags:
            memberships = database.execute('''SELECT 1 FROM pg_auth_members
                WHERE member=(SELECT oid FROM pg_roles WHERE rolname=%s) LIMIT 1''', (identity,)).fetchone()
            ownership = database.execute('''SELECT 1 FROM pg_shdepend
                WHERE refobjid=(SELECT oid FROM pg_roles WHERE rolname=%s) AND deptype='o' LIMIT 1''', (identity,)).fetchone()
            if memberships or ownership:
                raise ValueError('API reader must not inherit other roles or own database objects')
        action = 'ALTER' if flags else 'CREATE'
        database.execute(sql.SQL(action + ' ROLE {} LOGIN PASSWORD {} NOSUPERUSER NOCREATEDB NOCREATEROLE '
                                 'NOINHERIT NOREPLICATION NOBYPASSRLS').format(sql.Identifier(identity), sql.Literal(password)))
        database.execute(sql.SQL('ALTER ROLE {} SET default_transaction_read_only = on').format(sql.Identifier(identity)))
        database.execute(sql.SQL('GRANT CONNECT ON DATABASE {} TO {}').format(
            sql.Identifier(unquote(writer_url.path.lstrip('/'))), sql.Identifier(identity)))
        for schema in ['atlas', 'sections']:
            database.execute(sql.SQL('REVOKE ALL ON SCHEMA {} FROM {}').format(sql.Identifier(schema), sql.Identifier(identity)))
            database.execute(sql.SQL('GRANT USAGE ON SCHEMA {} TO {}').format(sql.Identifier(schema), sql.Identifier(identity)))
            database.execute(sql.SQL('REVOKE ALL ON ALL TABLES IN SCHEMA {} FROM {}').format(
                sql.Identifier(schema), sql.Identifier(identity)))
            database.execute(sql.SQL('GRANT SELECT ON ALL TABLES IN SCHEMA {} TO {}').format(
                sql.Identifier(schema), sql.Identifier(identity)))
            database.execute(sql.SQL('ALTER DEFAULT PRIVILEGES IN SCHEMA {} GRANT SELECT ON TABLES TO {}').format(
                sql.Identifier(schema), sql.Identifier(identity)))
    # Verify the credentials before persisting them. Never emit either connection URL.
    with psycopg.connect(url) as reader:
        reader.execute('SELECT COUNT(*) FROM atlas.municipalities')
    if not existing:
        path = root / '.env'
        content = path.read_text() if path.exists() else ''
        lines = [line for line in content.splitlines() if not line.strip().startswith('DATABASE_READ_URL=')]
        temporary = root / '.env.reader.pending'
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(descriptor, 'w') as output:
                output.write('\n'.join(lines) + '\nDATABASE_READ_URL=' + url + '\n')
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)
    return identity


def main() -> None:
    """Configure API read access as an explicit operation after schema migrations."""
    provision()
    print('API reader configured. DATABASE_READ_URL is stored privately; restart Nuxt to use it.')


if __name__ == '__main__':
    main()
