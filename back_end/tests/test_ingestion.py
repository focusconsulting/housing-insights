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
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             os.pardir)))

from housinginsights.ingestion.functions import load_meta_data
from housinginsights.tools import dbtools
from housinginsights.ingestion import DataReader, ManifestReader
from housinginsights.ingestion import CSVWriter
from housinginsights.ingestion.Cleaners import GenericCleaner


##########################################################################
## Tests
##########################################################################

class IngestionTests(unittest.TestCase):


    def test_can_run_tests(self):
        """
        Make sure that tests works for test_ingestion.py
        """
        assert(True)


    def test_file_checking(self):
        '''
        Various quality assurance checks on the DataReader's validation functions
        - include_flag in manifest used properly to determine loading or skipping
        - CSV file being loaded has the expected number of fields as found in meta.json
        - convenience function should_file_be_loaded performs properly
        '''
        META_FILENAME = os.path.join(os.path.dirname(__file__), 'test_data/meta_sample.json')
        meta = load_meta_data(META_FILENAME)
        table_name = 'buildings'

        MANIFEST_FILENAME = os.path.join(os.path.dirname(__file__), 'test_data/manifest_sample.csv')
        manifest = ManifestReader(MANIFEST_FILENAME)

        for manifest_row in manifest:
            print(manifest_row)
            csv_reader = DataReader(meta = meta, manifest_row=manifest_row)
            assert(csv_reader._do_fields_match())
            
             #assume they exactly match for the purpose of this test, expect as modified below
            sql_manifest_row = manifest_row
            #sql_manifest_row has an extra field to indicate whether it has been successfully loaded in previous runs or not
            sql_manifest_row['status'] = 'failed'

            if manifest_row['include_flag'] == "skip":
                self.assertFalse(csv_reader._check_include_flag(sql_manifest_row))
                self.assertFalse(csv_reader.should_file_be_loaded(sql_manifest_row))
            elif manifest_row['include_flag'] == "use":
                self.assertTrue(csv_reader._check_include_flag(sql_manifest_row))
                self.assertTrue(csv_reader.should_file_be_loaded(sql_manifest_row))

            #If the file is already in the SQL manifest, skip it when manifest says 'use' (i.e. it's already loaded)
            sql_manifest_row['status'] = 'loaded'
            if manifest_row['include_flag'] == "use":
                self.assertFalse(csv_reader._check_include_flag(sql_manifest_row))
            



    def test_unique_manifest_ids(self):
        '''Make sure the 'unique_data_id' column in the manifest is unique to each row'''
        #Example with all unique values
        MANIFEST_FILENAME = os.path.join(os.path.dirname(__file__), 'test_data/manifest_unique.csv')
        manifest1 = ManifestReader(MANIFEST_FILENAME)
        self.assertTrue(manifest1.has_unique_ids())

        #Example with a duplicated name
        MANIFEST_FILENAME = os.path.join(os.path.dirname(__file__), 'test_data/manifest_duplicates.csv')
        manifest2 = ManifestReader(MANIFEST_FILENAME)
        self.assertFalse(manifest2.has_unique_ids())
