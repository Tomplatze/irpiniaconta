"""Verify PostgreSQL enforces API read access even outside a read-only transaction."""
import unittest

import psycopg

from etl.settings import environment_value


@unittest.skipUnless(environment_value('DATABASE_READ_URL'), 'Run db:reader to configure the API login')
class ReaderPrivilegesTests(unittest.TestCase):
    def test_reader_can_read_both_publication_schemas(self):
        with psycopg.connect(environment_value('DATABASE_READ_URL')) as reader:
            self.assertEqual(reader.execute('SELECT COUNT(*) FROM atlas.municipalities').fetchone()[0], 118)
            self.assertEqual(reader.execute('SELECT COUNT(*) FROM sections.municipalities').fetchone()[0], 118)

    def test_reader_cannot_write_create_or_truncate_even_when_transaction_is_writable(self):
        with psycopg.connect(environment_value('DATABASE_READ_URL')) as reader:
            for statement in ['UPDATE atlas.observations SET value=value WHERE false',
                              'TRUNCATE sections.values_monthly',
                              'CREATE TABLE atlas.reader_must_not_create (id integer)']:
                with self.subTest(statement=statement), reader.transaction(force_rollback=True):
                    reader.execute('SET TRANSACTION READ WRITE')
                    with self.assertRaises(psycopg.errors.InsufficientPrivilege):
                        reader.execute(statement)


if __name__ == '__main__':
    unittest.main()
