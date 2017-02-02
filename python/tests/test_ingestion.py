##########################################################################
## Ingestion Package Tests
##########################################################################

# to execute tests, cd to the /python folder. This runs all test packages
# (this one and any other in the /tests folder)
#
#   nosetests --verbosity=2 --with-coverage --cover-inclusive --cover-erase tests
#
# for a list of available asserts:
# https://docs.python.org/2/library/unittest.html#assert-methods




##########################################################################
## Imports
##########################################################################

import unittest
from unittest import skip


import sys, os
sys.path.append(os.path.abspath('./'))

#Example import from our data structure
from housinginsights import ingestion
from housinginsights.ingestion import load_data
from housinginsights import tools



#from ingestion.load_data import MyObjectName

##########################################################################
## Tests
##########################################################################

class IngestionTests(unittest.TestCase):


    def test_can_run_tests(self):
        """
        Make sure that tests works for test_ingestion.py
        """
        print("I am running")
        assert(True)


    def test_do_fields_match(self):
        META_FILENAME = os.path.join(os.path.dirname(__file__), 'test_data/meta.json')
        meta = ingestion.load_data.load_meta_data(META_FILENAME)
        table_name = 'buildings'

        #check when they match completely:
        data_row = { 'Nlihc_id': 'a name', 'Status': 'a date', 'Rent': 132.5}
        assert(load_data.do_fields_match(data_row, meta, table_name))

         #check when csv has extra data:
        data_row = { 'Nlihc_id': 'a name', 'Status': 'a date', 'Rent': 132.5, 'extra_column': 'data'}
        self.assertFalse(load_data.do_fields_match(data_row, meta, table_name))

        #check when csv has missing data:
        data_row = { 'Nlihc_id': 'a name', 'Status': 'a date'}
        self.assertFalse(load_data.do_fields_match(data_row, meta, table_name))

    def test_unique_manifest_ids(self):

        #Check that non-duplicated at returns True
        MANIFEST_FILENAME = os.path.join(os.path.dirname(__file__), 'test_data/manifest_unique.csv')
        test = load_data.check_csv_manifest_unique_ids(MANIFEST_FILENAME)
        self.assertTrue(test)

        #check that duplicated unique_data_id returns False
        MANIFEST_FILENAME = os.path.join(os.path.dirname(__file__), 'test_data/manifest_duplicates.csv')
        test = load_data.check_csv_manifest_unique_ids(MANIFEST_FILENAME)
        self.assertFalse(test)


    #TODO this needs to be completed. Need to set up database w/ sample data
    def test_get_sql_manifest_row(self):
        database_connection = tools.database.get_database_connection('local_database')
        MANIFEST_FILENAME = os.path.join(os.path.dirname(__file__), 'test_data/manifest_unique.csv')

        csv_manifest = ingestion.load_data.read_csv_manifest(MANIFEST_FILENAME)
       
        #only need one row
        csv_row_1 = next(csv_manifest)
        sql_row = load_data.get_sql_manifest_row(database_connection = database_connection, csv_row = csv_row_1)

        assert(True)