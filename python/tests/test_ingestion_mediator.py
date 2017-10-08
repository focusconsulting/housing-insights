import unittest
import os
import sys

from python.housinginsights.tools.ingestion_mediator import IngestionMediator
from python.housinginsights.ingestion.LoadData import LoadData
from python.housinginsights.ingestion.Manifest import Manifest
from python.housinginsights.ingestion.Meta import Meta
from python.housinginsights.ingestion.SQLWriter import HISql
from python.scripts.get_api_data import GetApiData

PYTHON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           os.pardir))
# sys.path.append(PYTHON_PATH)
SCRIPTS_PATH = os.path.abspath(os.path.join(PYTHON_PATH, 'scripts'))


class MyTestCase(unittest.TestCase):
    def setUp(self):
        manifest_path = os.path.abspath(os.path.join(SCRIPTS_PATH,
                                                     'manifest.csv'))
        # initialize mediator and colleague instances
        self.load_data = LoadData(debug=True)
        self.mediator = IngestionMediator(debug=True)
        self.manifest = Manifest(manifest_path)
        self.meta = Meta()
        self.hisql = HISql(debug=True)
        self.get_api_data = GetApiData(debug=True)

        # build connection between mediator and its colleagues
        self.load_data.set_ingestion_mediator(self.mediator)
        self.mediator.set_load_data(self.load_data)
        self.manifest.set_ingestion_mediator(self.mediator)
        self.mediator.set_manifest(self.manifest)
        self.meta.set_ingestion_mediator(self.mediator)
        self.mediator.set_meta(self.meta)
        self.hisql.set_ingestion_mediator(self.mediator)
        self.mediator.set_hi_sql(self.hisql)
        self.get_api_data.set_ingestion_mediator(self.mediator)
        self.mediator.set_get_api_data(self.get_api_data)

        # get db engine
        self.engine = self.mediator.get_engine()

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

    def test_LoadData_load_cleaned_data(self):
        # case - invalid unique_data_id passed
        self.assertRaises(ValueError, self.load_data.load_cleaned_data,
                          ['fake'])

        # case - missing psv with use_raw_if_missing = False
        # delete file first if already exists
        psv_path = self.mediator.get_clean_psv_path('dchousing_project')
        if psv_path is not None:
            os.remove(psv_path)
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

    def test_LoadData_reload_all_from_manifest(self):
        self.load_data.reload_all_from_manifest(drop_tables=True)

        # verify resulting sql_manifest post database rebuild
        with self.engine.connect() as conn:
            q = 'select unique_data_id, destination_table, status FROM manifest'
            q_result = conn.execute(q)
            result = {row[0]: {
                'destination_table': row[1], 'status': row[2]}
                for row in q_result.fetchall()}

        for unique_data_id in result:
            manifest_row = self.manifest.get_manifest_row(unique_data_id)
            manifest_table_name = manifest_row['destination_table']
            result_table_name = result[unique_data_id]['destination_table']
            result_status = result[unique_data_id]['status']
            self.assertEqual(manifest_table_name, result_table_name,
                             'should have matching table name: {} : {}'.format(
                                 manifest_table_name, result_table_name))
            self.assertEqual('loaded', result_status,
                             'should have status = loaded: actual {}'.format(
                                 result_status))

    def test_LoadData_recalculate_database(self):
        # make sure database is populated with all tables
        self.load_data.reload_all_from_manifest()

        # make sure zone_facts is not in db
        if 'zone_facts' in self.engine.table_names():
            with self.engine.connect() as conn:
                conn.execute('DROP TABLE zone_facts;')

        # currently no zone_facts table
        result = 'zone_facts' in self.engine.table_names()
        self.assertFalse(result, 'zone_facts table is not in db')

        # rebuild zone_facts table
        result = self.load_data.recalculate_database()
        self.assertTrue(result, 'should have loaded zone_facts table')

        # confirm zone_facts table was loaded into db
        result = 'zone_facts' in self.engine.table_names()
        self.assertTrue(result, 'zone_facts table is in db')

    def test_GetApiData_get_files_by_modules(self):
        # case - invalid module
        result = self.get_api_data.get_files_by_modules(['fake'])
        self.assertFalse(result, 'should return empty result: %s' % result)
        self.assertEqual(len(result), 0, 'should return empty result')

        # case - single module
        result = self.get_api_data.get_files_by_modules(['DCHousing'])
        self.assertTrue(result, 'should return non-empty result: %s' % result)
        self.assertTrue('DCHousing' in result, 'should return DCHousing as '
                                               'processed in result')
        self.assertEqual(len(result), 1, 'should return a single result')

        # case - multiple modules
        modules_list = ['opendata', 'dhcd']
        result = self.get_api_data.get_files_by_modules(modules_list)
        self.assertTrue(result, 'should return non-empty result: %s' % result)
        for mod in modules_list:
            self.assertTrue(mod in result,
                            'should return same values as original: '
                            '{} is missing'.format(mod))
        self.assertEqual(len(result), 2, 'should return two values in result')

    def test_GetApiData_get_files_by_data_ids(self):
        # case - invalid data id
        result = self.get_api_data.get_files_by_data_ids(['fake'])
        self.assertFalse(result, 'should return empty result: %s' % result)
        self.assertEqual(len(result), 0, 'should return empty result')

        # case - single data id
        result = self.get_api_data.get_files_by_data_ids(['dchousing'])
        self.assertTrue(result, 'should return non-empty result: %s' % result)
        self.assertTrue('dchousing' in result, 'should return dchousing as '
                                               'processed in result')
        self.assertEqual(len(result), 1, 'should return a single result')

        # case - multiple data ids
        modules_list = ['crime_2015', 'building_permits_2016']
        result = self.get_api_data.get_files_by_data_ids(modules_list)
        self.assertTrue(result, 'should return non-empty result: %s' % result)
        for mod in modules_list:
            self.assertTrue(mod in result,
                            'should return same values as original: '
                            '{} is missing'.format(mod))
        self.assertEqual(len(result), 2, 'should return two values in result')


if __name__ == '__main__':
    unittest.main()
