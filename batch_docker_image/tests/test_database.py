import os
import sys

here = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(here)

import unittest
from unittest.mock import patch, MagicMock
import pg8000

from database import setup_database_connection, create_database_schema

class TestDatabaseConnection(unittest.TestCase):
    @patch.dict(os.environ, {
        'DB_NAME': 'test_db',
        'DB_HOST': 'test_host',
        'DB_PORT': '5432'
    })
    @patch('pg8000.connect')
    def test_setup_database_connection(self, mock_connect):
        secret = {'username': 'test_user', 'password': 'test_password'}
        setup_database_connection(secret)
        mock_connect.assert_called_with(
            database='test_db',
            host='test_host',
            port=5432,
            user='test_user',
            password='test_password'
        )

class TestDatabaseSchema(unittest.TestCase):
    def setUp(self):
        self.mock_conn = MagicMock()
        self.mock_cursor = self.mock_conn.cursor.return_value
        self.mock_cursor.__enter__.return_value = self.mock_cursor

    def test_create_database_schema(self):
        create_database_schema(self.mock_conn)
        self.mock_cursor.execute.assert_has_calls([
            unittest.mock.call("CREATE EXTENSION IF NOT EXISTS vector;"),
            unittest.mock.call(unittest.mock.ANY)
        ])
        self.mock_conn.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()