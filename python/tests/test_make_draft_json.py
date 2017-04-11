import unittest
from unittest.mock import patch, MagicMock
from housinginsights.ingestion.make_draft_json import (sql_name_clean, pandas_to_sql_data_type,
                                                       make_draft_json, make_all_json)


class dataframe_file:
    columns = ['foo', 'bar']


class TestMakeDraftJson(unittest.TestCase):
    """ Unit tests for ``make_draft_json.py``. """

    def setUp(self):
        self.name = 'FOO-bar'
        self.pandas_type_string = 'int64'
        self.filename = 'test'
        self.tablename = 'test'
        self.manifest_path = 'test'

    def test_sql_name_clean(self):
        result = sql_name_clean(self.name)
        self.assertEqual(result, 'foo_bar')

    def test_pandas_to_sqal_data_type(self):
        exists = pandas_to_sql_data_type(self.pandas_type_string)
        self.assertEqual(exists, 'integer')

        not_exists = pandas_to_sql_data_type('something')
        self.assertEqual(not_exists, 'text')

    @patch('housinginsights.ingestion.make_draft_json.open')
    @patch('housinginsights.ingestion.make_draft_json.pandas_to_sql_data_type')
    @patch('housinginsights.ingestion.make_draft_json.pandas.read_csv')
    def test_make_draft_json(self, mock_read_csv, mock_pandas_to_sql_data_type, mock_open):
        """ TODO:  Still needs more tests.

            This is a tricky one to test, there are a lot of external dependencies
            and global variables that make testing tricky.

            Consider re-factoring this function.
        """
        make_draft_json(self.filename, self.tablename)
        mock_read_csv.assert_called_with(self.filename, encoding='latin1')

    @patch('housinginsights.ingestion.make_draft_json.ManifestReader')
    def test_make_all_json(self, mock_manifest):
        """ TODO:  Still needs more tests.

            Need to test with sample Manifest data.
        """
        make_all_json(self.manifest_path)
        mock_manifest.assert_called_with(path=self.manifest_path)
