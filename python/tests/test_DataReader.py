import sys, os
import unittest
sys.path.append(os.path.abspath('../'))

from housinginsights.ingestion.DataReader import DataReader
from housinginsights.tools import dbtools

from housinginsights.ingestion import DataReader, ManifestReader
from housinginsights.ingestion import CSVWriter, DataReader
from housinginsights.ingestion import HISql, TableWritingError
from housinginsights.ingestion import functions as ingestionfunctions

# SETUP - Mostly taken from load_data.py
meta_path = 'test_data/meta.json' # TODO Update when meta.json is updated.
manifest_path = 'test_data/manifest_unique.csv' # TODO Consider updating manifest_sample
database_choice = 'docker_database'
logging_path = os.path.abspath("../logs")

meta = ingestionfunctions.load_meta_data(meta_path)
engine = dbtools.get_database_engine(database_choice)
manifest = ManifestReader(manifest_path)

FAKE_REQUIRED_FIELD = {'sql_name': 'foo', 'type': 'decimal', 'source_name': 'FAKE_REQUIRED', 'display_text': 'Blah', 'display_name': 'x',
                'required_in_source': True}
FAKE_OPTIONAL_FIELD = {'sql_name': 'foo', 'type': 'decimal', 'source_name': 'FAKE_OPTIONAL', 'display_text': 'Blah', 'display_name': 'x',
                'required_in_source': False}

class TestVerifyRequiredMetadata(unittest.TestCase):
    def test_verify_required_metadata_columns(self):
        manifest_row, csv_reader = prep_manifest_row_and_csv_reader()
        sql_manifest_row = prep_sql_manifest_row(manifest_row)
        field_list = csv_reader.meta[csv_reader.destination_table]['fields']

        # Baseline assertions
        self.assertTrue(csv_reader.verify_required_metadata_columns_exist_in_actual(field_list))

        # Test that if an optional column does not exist in actual dataset, verify_required_metadata_columns_exist_in_actual still returns True.
        field_list.append(FAKE_OPTIONAL_FIELD)
        self.assertTrue(csv_reader.verify_required_metadata_columns_exist_in_actual(field_list)) # Assert True!

        # Test that if a mandatory column does not exist in actual dataset, verify_required_metadata_columns_exist_in_actual returns False.
        field_list.append(FAKE_REQUIRED_FIELD)
        self.assertFalse(csv_reader.verify_required_metadata_columns_exist_in_actual(field_list)) # Assert False!

        # TODO Test that if an actual csv column does not exist in metadata, verify_actual_columns_exist_in_metadata returns False.
        # Not sure how to write this one, since modifying keys property doesn't seem to work
        # and I don't want to modify any of the csvs. Consider setting up fixtures for these types of tests.


# Setup functions replicate certain logic from load_data.py
# to help us properly instantiate the required objects.
def prep_manifest_row_and_csv_reader():
    for manifest_row in manifest:
        if manifest_row['include_flag'] == 'use':
            temp_filepath = os.path.abspath(
                                os.path.join(
                                    logging_path,
                                    'temp_{}.psv'.format(manifest_row['unique_data_id'])
                                ))
            csv_reader = DataReader(meta = meta, manifest_row=manifest_row, load_from="file")
            return manifest_row, csv_reader

def prep_sql_manifest_row(manifest_row):
    temp_filepath = os.path.abspath(
                        os.path.join(
                            logging_path,
                            'temp_{}.psv'.format(manifest_row['unique_data_id'])
                        ))
    sql_interface = HISql(meta = meta, manifest_row = manifest_row, engine = engine, filename=temp_filepath)
    sql_manifest_row = sql_interface.get_sql_manifest_row()
    return sql_manifest_row

if __name__ == '__main__':
    unittest.main()
