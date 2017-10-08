import unittest
import os
import sys

from python.housinginsights.tools.ingestion_mediator import IngestionMediator
from python.housinginsights.ingestion.LoadData import LoadData
from python.housinginsights.ingestion.Manifest import Manifest
from python.housinginsights.ingestion.Meta import Meta
from python.housinginsights.ingestion.SQLWriter import HISql

PYTHON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           os.pardir))
# sys.path.append(PYTHON_PATH)
SCRIPTS_PATH = os.path.abspath(os.path.join(PYTHON_PATH, 'scripts'))


class MyTestCase(unittest.TestCase):
    def setUp(self):
        manifest_path = os.path.abspath(os.path.join(SCRIPTS_PATH,
                                                     'manifest.csv'))
        # initialize mediator and colleague instances
        self.load_data = LoadData(debug=True, drop_from_table=True)
        self.mediator = IngestionMediator(debug=True)
        self.manifest = Manifest(manifest_path)
        self.meta = Meta()
        self.hisql = HISql(debug=True)

        # build connection between mediator and its colleagues
        self.load_data.set_ingestion_mediator(self.mediator)
        self.mediator.set_load_data(self.load_data)
        self.manifest.set_ingestion_mediator(self.mediator)
        self.mediator.set_manifest(self.manifest)
        self.meta.set_ingestion_mediator(self.mediator)
        self.mediator.set_meta(self.meta)
        self.hisql.set_ingestion_mediator(self.mediator)
        self.mediator.set_hi_sql(self.hisql)

    def test_get_clean_psv_path(self):
        # case - invalid unique_data_id passed
        result = self.mediator.get_clean_psv_path('fake')
        self.assertIsNone(result, 'should return None')

        # case - valid unique_data_id passed
        result = self.mediator.get_clean_psv_path('mar')
        self.assertIsNotNone(result, 'should not return None')
        self.assertTrue(result, 'should return a path')
        self.assertTrue(os.path.exists(result), 'should return a path that '
                                                'exists')

    def test_process_and_clean_raw_data(self):
        # case - invalid unique_data_id passed
        self.assertRaises(ValueError, self.mediator.process_and_clean_raw_data,
                          'fake')

        # case - valid unique_data_id passed
        result = self.mediator.process_and_clean_raw_data('mar')
        self.assertTrue(result, 'should return a result')
        self.assertTrue(os.path.exists(result), 'should return a path that '
                                                'exists')

        # case - invalid unique_data_id passed with debug = False
        self.mediator.set_debug(False)
        result = self.mediator.process_and_clean_raw_data('fake')
        self.assertIsNone(result, 'should return None')

    def test_LoadData_load_raw_data(self):
        # case - invalid unique_data_id passed
        self.assertRaises(ValueError, self.load_data.load_raw_data, ['fake'])

        # case - pass empty unique_data_id_list
        result = self.load_data.load_raw_data([])
        self.assertFalse(result, 'should return empty list')
        self.assertEqual(len(result), 0, 'should return empty list')

        # case - single unique_data_id passed
        result = self.load_data.load_raw_data(['mar'])
        self.assertTrue(result, 'should return a non-empty list')
        self.assertEqual(len(result), 1, 'should return a list with len = 1')
        self.assertTrue('mar' in result, '"mar" should be only value is list')

        # case - multiple unique_data_ids passed
        unique_data_id_list = ['mar', 'prescat_project',
                               'dhcd_dfd_properties_addre', 'dchousing_subsidy']
        result = self.load_data.load_raw_data(unique_data_id_list)
        self.assertTrue(result, 'should return a non-empty list')
        self.assertEqual(len(result), len(unique_data_id_list),
                         'should return a list with same length as original')
        for uid in unique_data_id_list:
            self.assertTrue(uid in result,
                            '"{}" should be only value is list'.format(uid))

        # case - invalid unique_data_id passed with debug=False
        self.mediator.set_debug(False)
        result = self.load_data.load_raw_data(['fake'])
        self.assertFalse(result, 'should return empty list')
        self.assertEqual(len(result), 0, 'should be empty list')

    def test_LoadData_lead_cleaned_data(self):
        # case - invalid unique_data_id passed
        self.assertRaises(ValueError, self.load_data.load_cleaned_data,
                          ['fake'])

        # case - missing psv with use_raw_if_missing = False
        self.assertRaises(FileNotFoundError, self.load_data.load_cleaned_data,
                          ['dchousing_project'], use_raw_if_missing=False)

        # case - pass empty unique_data_id_list
        result = self.load_data.load_cleaned_data([])
        self.assertFalse(result, 'should return empty list')
        self.assertEqual(len(result), 0, 'should return empty list')

        # case - single unique_data_id passed
        result = self.load_data.load_cleaned_data(['mar'])
        self.assertTrue(result, 'should return a non-empty list')
        self.assertEqual(len(result), 1, 'should return a list with len = 1')
        self.assertTrue('mar' in result, '"mar" should be only value is list')

        # case - multiple unique_data_ids passed
        unique_data_id_list = ['mar', 'prescat_project',
                               'dhcd_dfd_properties_addre', 'dchousing_subsidy']
        result = self.load_data.load_cleaned_data(unique_data_id_list)
        self.assertTrue(result, 'should return a non-empty list')
        self.assertEqual(len(result), len(unique_data_id_list),
                         'should return a list with same length as original')
        for uid in unique_data_id_list:
            self.assertTrue(uid in result,
                            '"{}" should be only value is list'.format(uid))

        # case - invalid unique_data_id passed with debug=False
        self.mediator.set_debug(False)
        result = self.load_data.load_cleaned_data(['fake'])
        self.assertFalse(result, 'should return empty list')
        self.assertEqual(len(result), 0, 'should be empty list')


if __name__ == '__main__':
    unittest.main()
