import unittest
import os
from python.housinginsights.ingestion import LoadData as load_data
from sqlalchemy.exc import ProgrammingError

PYTHON_PATH = load_data.PYTHON_PATH


class MyTestCase(unittest.TestCase):
    def setUp(self):
        # use test data
        test_data_path = os.path.abspath(os.path.join(PYTHON_PATH, 'tests',
                                                      'test_data'))
        self.meta_path = os.path.abspath(os.path.join(test_data_path,
                                                      'meta_load_data.json'))
        self.manifest_path = os.path.abspath(
            os.path.join(test_data_path, 'manifest_load_data.csv'))
        self.database_choice = 'docker_database'
        self.loader = load_data.LoadData(database_choice=self.database_choice,
                                         meta_path=self.meta_path,
                                         manifest_path=self.manifest_path)

    def query_db(self, engine, query):
        """
        Helper function that returns the result of querying the database.
        """
        try:
            query_result = engine.execute(query)
            return [dict(x) for x in query_result.fetchall()]
        except ProgrammingError as e:
            self.assertEqual(True, False, e)

    def test_update_only(self):
        # use the same sql engine for db lookup
        loader_engine = self.loader.engine

        # start with empty database
        self.loader._drop_tables()
        result = loader_engine.table_names()
        self.assertEqual(len(result), 0)

        # load crime data one at a time without overriding
        # existing data
        crime_data = ['crime_2016', 'crime_2015', 'crime_2017']
        table_name = 'crime'

        for idx, data_id in enumerate(crime_data, start=1):
            these_data = [data_id]
            result = self.loader.update_database(unique_data_id_list=these_data)
            self.assertTrue(data_id in result)

            # validate database contents
            query = "SELECT DISTINCT unique_data_id FROM crime"
            results = self.query_db(loader_engine, query)

            self.assertEqual(len(results), idx)

            for result in results:
                self.assertTrue(result['unique_data_id'] in crime_data)

        # there's only 'crime' and manifest table in database
        result = loader_engine.table_names()
        self.assertEqual(len(result), 2)
        self.assertTrue(table_name in result)
        self.assertTrue('manifest' in result)

        # make sure database is not empty
        self.loader.rebuild()
        result = loader_engine.table_names()
        self.assertTrue(len(result) > 0)

        # update sample of data_ids and make sure no duplications
        these_data = ['project', 'crime_2017', 'dchousing_subsidy']

        # get current table and unique_data_id row counts
        tables = ['project', 'crime', 'subsidy']
        tables_row_counts = []
        data_id_row_counts = []

        for idx, table in enumerate(tables):
            # get table counts
            query = "SELECT COUNT(*) FROM {}".format(table)
            result = self.query_db(loader_engine, query)
            tables_row_counts.append(result[0]['count'])

            # get unique_data_id counts
            query = "SELECT COUNT(*) FROM {} WHERE unique_data_id = " \
                    "'{}'".format(table, these_data[idx])
            result = self.query_db(loader_engine, query)
            data_id_row_counts.append(result[0]['count'])

        processed_data_id = self.loader.update_database(these_data)

        for data_id in these_data:
            self.assertTrue(data_id in processed_data_id)

        for idx, table in enumerate(tables):
            # get updated table counts
            query = "SELECT COUNT(*) FROM {}".format(table)
            result = self.query_db(loader_engine, query)
            self.assertEqual(result[0]['count'], tables_row_counts[idx])

            # get updated unique_data_id counts
            query = "SELECT COUNT(*) FROM {} WHERE unique_data_id = " \
                    "'{}'".format(table, these_data[idx])
            result = self.query_db(loader_engine, query)
            self.assertEqual(result[0]['count'], data_id_row_counts[idx])

    def test_create_list(self):
        # Note - you will need to modify folder path to match local env
        folder_path = os.path.join(PYTHON_PATH, os.pardir, 'data', 'raw',
                                   'apis', '20170528')
        result = self.loader.create_list(folder_path)
        print(result)
        self.assertEqual(len(result), 13)

    def test_rebuild(self):
        result = self.loader.rebuild()
        self.assertTrue(result)

    def test_make_manifest(self):
        folder_path = os.path.join(PYTHON_PATH, os.pardir, 'data', 'raw',
                                   'apis')
        fields = self.loader.manifest.keys
        print(fields)
        self.assertTrue(fields)
        result_path = self.loader.make_manifest(folder_path)
        self.assertEqual(self.loader.manifest.path, result_path)

    def test__get_zone_fact_zones(self):
        ward_types = self.loader._get_zone_specifics_for_zone_type('ward')

        for idx in range(9):
            ward = "Ward " + str(idx) if idx > 0 else 'ward'
            self.assertTrue(ward in ward_types)

    def test__create_zone_facts_table(self):
        print(self.loader.engine.table_names())
        print(self.loader._create_zone_facts_table())
        print(self.loader.engine.table_names())
        result = 'zone_facts' in self.loader.engine.table_names()
        self.assertTrue(result, 'zone_facts table is in db')

    def test__get_weighted_census_results(self):
        grouping = 'ward'
        field = 'population_poverty'
        data_id = 'poverty_rate'

        numerator = self.loader._get_weighted_census_results(grouping,
                                                             field)
        print(numerator)
        print()
        denominator = self.loader._get_weighted_census_results(grouping,
                                                               'population')
        print(denominator)
        print()
        result = self.loader._items_divide(numerator, denominator)
        print(result)
        print()

        result = self.loader._census_with_weighting(data_id, grouping)
        print(result)

        self.assertEqual(True, False)

    def test__add_census_with_weighting_fields_to_zone_facts_table(self):
        self.loader._create_zone_facts_table()
        result = self.loader\
            ._add_census_with_weighting_fields_to_zone_facts_table()
        print(result)

        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
