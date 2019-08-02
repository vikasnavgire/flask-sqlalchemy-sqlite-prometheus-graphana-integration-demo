"""Tests for Basic Functions"""
import sys
import json
import unittest
from unittest.mock import patch

sys.path.append("../..")
from app import *

from tests.test_variables_responses import *


class TestFunctions(unittest.TestCase):
    """Test case for the client methods."""

    def setup(self):
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()

    def test_getKeys_unauthorised(self):
        with app.test_request_context():
            message, status_code = getKeys()
            exp_response = ('Unauthorised ', 403)
            self.assertEqual((message, status_code), exp_response)

    @patch('app.get_query_result')
    def test_getKeys_authorized(self, mock_get_query_result):
        with app.test_request_context(headers=headers):
            mock_get_query_result.return_value = get_query_result
            message, status_code = getKeys()
            self.assertEqual(status_code, 200)

    @patch('app.get_query_result')
    def test_getKeys_id(self, mock_get_query_result):
        with app.test_request_context(headers=headers):
            mock_get_query_result.return_value = get_query_result_key
            message, status_code = getKeys(4)
            self.assertEqual(status_code, 200)
            self.assertEqual(message.data, exp_4_resp)

    @patch('app.get_query_result')
    def test_getKeys_filter(self, mock_get_query_result):
        with app.test_request_context(headers=headers) as req:
            req.request.args = {'filter': 'soh%'}
            mock_get_query_result.return_value = get_query_result_filter
            message, status_code = getKeys()
            self.assertEqual(status_code, 200)
            self.assertIsNotNone(message.data)

    @patch('app.get_query_result')
    def test_getKeys_exc(self, mock_get_query_result):
        with app.test_request_context(headers=headers):
            mock_get_query_result.return_value = 123
            res, code  = getKeys()
            self.assertEqual(code, 500)

    @patch('app.db.session.commit')
    @patch('app.db.session.add')
    def test_putKeys(self, mock_add, mock_comm):
        with app.test_request_context(headers=headers) as req:
            mock_add.return_value = None
            mock_comm.return_value = None
            req.request.data = b"vikas"
            res = putKeys()
            self.assertEqual(res.data, b'"record added"\n')

    @patch('app.db.session.commit')
    @patch('app.db.session.add')
    def test_putKeys(self, mock_add, mock_comm):
        with app.test_request_context(headers=headers) as req:
            req.request.args = {'expire_in': 100}
            mock_add.return_value = None
            mock_comm.return_value = None
            req.request.data = b"vikas"
            res = putKeys()
            self.assertEqual(res.data, b'"record added"\n')

    @patch('app.db.session.commit')
    @patch('app.db.session.add')
    def test_putKeys_exc(self, mock_add, mock_comm):
        with app.test_request_context(headers=headers) as req:
            mock_add.return_value = None
            mock_comm.return_value = None
            req.request.data = "vikas"
            res, code = putKeys()
            self.assertEqual(code, 500)

    @patch('app.db.session.query')
    def test_deleteKeys_id(self, mock_query):
        with app.test_request_context(headers=headers):
            mock_query.return_value.filter.return_value.delete.return_value = 1
            res = deleteKeys(1)
            self.assertEqual(res.data, b'{\n  "row_affected": 1\n}\n')

    @patch('app.db.session.query')
    def test_deleteKeys_all(self, mock_query):
        with app.test_request_context(headers=headers):
            mock_query.return_value.delete.return_value = 5
            res = deleteKeys()
            self.assertEqual(res.data, b'{\n  "row_affected": 5\n}\n')

    @patch('app.db')
    def test_deleteKeys_exc(self, mock_query):
        with app.test_request_context(headers=headers):
            mock_query.return_value = 1
            res, code = deleteKeys(1)
            self.assertEqual(code, 500)

if __name__ == '__main__':
    unittest.main()
