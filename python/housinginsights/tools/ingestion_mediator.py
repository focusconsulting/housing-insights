"""
This module is an implementation of a mediator object. It interacts
 with all objects and scripts involved in our ingestion and processing
 protocol and coordinate their activities.

 The following are some core tasks:

    - check for new data regularly per specific schedule or on demand when
    requested by admin
    - download and ingest all new data
    - handle all data ingestion problems via logging and skipping
    - alert amdins via email of the data collection status; any
    missing/skipped data sets, any ingestion problems
"""

# built-in import
import os
import sys
from time import time, sleep

# relative package import for when running as a script
PYTHON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           os.pardir, os.pardir))
# sys.path.append(PYTHON_PATH)
SCRIPTS_PATH = os.path.abspath(os.path.join(PYTHON_PATH, 'scripts'))
CLEAN_PSV_PATH = os.path.abspath(os.path.join(PYTHON_PATH, os.pardir,
                                              'data', 'processed',
                                              '_clean_psv'))

from python.housinginsights.ingestion.DataReader import DataReader
from python.housinginsights.ingestion.LoadData import LoadData
from python.housinginsights.ingestion.Manifest import Manifest
from python.housinginsights.ingestion.Meta import Meta
from python.housinginsights.tools import dbtools
from python.housinginsights.ingestion.SQLWriter import HISql
from python.housinginsights.tools.logger import HILogger
from python.housinginsights.ingestion.CSVWriter import CSVWriter

logger = HILogger(name=__file__, logfile="ingestion_mediator.log")  # TODO -
# refactor


class IngestionMediator(object):
    def __init__(self, database_choice=None, debug=False):
        """
        Initialize mediator with private instance variables for colleague
        objects and other instance variables needed for ingestion workflow
        """
        # load defaults if no arguments passed
        if database_choice is None:
            self._database_choice = 'docker_database'
        else:
            self._database_choice = database_choice

        # initialize instance variables related from above passed args
        self._debug = debug
        self._engine = dbtools.get_database_engine(self._database_choice)
        self._manifest_row = None  # typically working on one at time - track?
        self._table_name = None

        # initialize instance variables for colleague objects
        self._load_data = None
        self._manifest = None
        self._meta = None
        self._hi_sql = None

    ###############################
    # setter methods for linking this instance with respective colleague
    # instances
    ###############################
    def set_load_data(self, load_data_instance):
        self._load_data = load_data_instance

    def set_manifest(self, manifest_instance):
        self._manifest = manifest_instance

    def set_meta(self, meta_instance):
        self._meta = meta_instance

    def set_hi_sql(self, hi_sql_instance):
        self._hi_sql = hi_sql_instance

    ###############################
    # setter and getter methods for accessing private instance variables
    ###############################
    def set_debug(self, debug):
        self._debug = debug

    def get_debug(self):
        return self._debug

    def get_engine(self):
        """
        Return the database engine associated with the instance of ingestion
        mediator.
        """
        return self._engine

    def get_current_manifest_row(self):
        return self._manifest_row

    def get_current_table_name(self):
        return self._table_name

    def get_clean_psv_path(self, unique_data_id):
        self._set_manifest_row_and_table_name(unique_data_id)
        clean_data_path = os.path.abspath(
            os.path.join(CLEAN_PSV_PATH,
                         'clean_{}.psv'.format(unique_data_id)))

        # check that it is valid file path and return accordingly
        if os.path.isfile(clean_data_path):
            return clean_data_path
        else:
            return None

    def _set_manifest_row_and_table_name(self, unique_data_id):
        self._manifest_row = self._manifest.get_manifest_row(unique_data_id)
        if self._manifest_row is not None:
            self._table_name = self._manifest_row['destination_table']
        else:
            self._table_name = None

    ###############################
    # instance methods for coordinating tasks across other objects
    ###############################
    # download new raw data
    def get_raw_data(self, manifest_row):
        pass

    # process and clean raw data
    def process_and_clean_raw_data(self, unique_data_id):
        """
        Processes and cleans the raw data file for the passed unique_data_id.

        Once processed and clean, the resulting clean_unique_dat_id.psv file
        path is returned as string.

        :param unique_data_id: the unique data id for the raw data file to be
        processed and cleaned
        :return: string representation of the path for the
        clean_unique_data_id.psv
        """
        self._manifest_row = self._manifest.get_manifest_row(unique_data_id)

        # validate resulting manifest_row
        if self._manifest_row is None:
            logger.error('"{}" is not in manifest.csv!'.format(unique_data_id))
            if self._debug:
                raise ValueError('"{}" is not a valid unique_data_id!'.format(
                    unique_data_id))
            else:
                return None

        self._table_name = self._manifest_row['destination_table']
        clean_data_path = os.path.abspath(
                    os.path.join(CLEAN_PSV_PATH,
                                 'clean_{}.psv'.format(unique_data_id)))
        raw_data_reader = DataReader(meta=self._meta.get_meta(),
                                     manifest_row=self._manifest_row)
        clean_data_writer = CSVWriter(meta=self._meta.get_meta(),
                                      manifest_row=self._manifest_row,
                                      filename=clean_data_path)
        cleaner = self._meta.get_cleaner_from_name(
            manifest_row=self._manifest_row, engine=self._engine)

        # clean the file and save the output to a local pipe-delimited file
        if raw_data_reader.should_file_be_loaded():
            logger.info("  Cleaning...")
            start_time = time()
            meta_only_fields = self._meta.get_meta_only_fields(
                table_name=self._table_name, data_fields=raw_data_reader.keys)
            total_rows = len(raw_data_reader)
            for idx, data_row in enumerate(raw_data_reader):
                if idx % 100 == 0:
                    print("  on row ~{} of {}".format(idx, total_rows),
                          end='\r', flush=True)

                try:
                    data_row.update(meta_only_fields)  # insert other field dict
                    clean_data_row = cleaner.clean(data_row, idx)
                    if clean_data_row is not None:
                        clean_data_writer.write(clean_data_row)
                except Exception as e:
                    logger.error("Error when trying to clean row index {} from"
                                 " the manifest_row {}".format(
                                  idx, self._manifest_row))
                    if self._debug is True:
                        raise e

            clean_data_writer.close()
            end_time = time()
            print("\nRun time= %s" % (end_time - start_time))

        return clean_data_path

    # write file to db
    def write_file_to_db(self, unique_data_id, clean_data_path):
        # update instance with correct self._manifest_row and self._table_name
        self._set_manifest_row_and_table_name(unique_data_id)

        # remove existing data
        result = self._hi_sql.remove_existing_data(self._manifest_row,
                                                   self._engine)

        # remove table if necessary
        if result is not None:
            _ = self._hi_sql.remove_table_if_empty(self._manifest_row,
                                                   self._engine)

        # create table if it doesn't exist
        if self._hi_sql.does_table_exist(self._table_name, self._engine):
            logger.info("Did not create table because it already exists")
        else:
            sql_fields, sql_field_types = \
                self._meta.get_sql_fields_and_type_from_meta(self._table_name)
            self._hi_sql.create_table(self._table_name, sql_fields,
                                      sql_field_types, self._engine)

        # load clean file to database
        return self._hi_sql.write_file_to_sql(self._table_name,
                                              clean_data_path, self._engine)


if __name__ == '__main__':
    # initialize instances to be used for this ingestion mediator instance
    load_data = LoadData(drop_from_table=True)
    manifest = Manifest(os.path.abspath(os.path.join(SCRIPTS_PATH,
                                                     'manifest.csv')))
    meta = Meta()
    hisql = HISql()

    # initialize an instance of ingestion mediator and set colleague instances
    mediator = IngestionMediator()
    mediator.set_load_data(load_data)
    mediator.set_manifest(manifest)
    mediator.set_meta(meta)
    mediator.set_hi_sql(hisql)

    # connect colleague instances to this ingestion mediator instance
    load_data.set_ingestion_mediator(mediator)
    manifest.set_ingestion_mediator(mediator)
    meta.set_ingestion_mediator(mediator)
    hisql.set_ingestion_mediator(mediator)
