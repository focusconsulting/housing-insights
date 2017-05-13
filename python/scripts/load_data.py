"""
Modulel loads our flat file data into the Postgres database. It will rebuild the
database of choice with sample or real data by first deleting any data in the
repository, and then re-load the data into the repository.

If you want to rebuild the data with actual data (i.e. what is in manifest.csv
instead of manifest.csv), run the same command without ‘sample’ at the end.

Notes:
 - manifest.csv has every flat file that needs to be loaded (i.e. CSV's we have
 downloaded).
 - other scripts can get data that is available from APIs, so manifest won't
 reflect all the data we are including.
 - meta.json provides meta information about our *SQL* tables. Note that
 because multiple CSV's can go into the same table (i.e. two different versions
 of the same data), there will be more rows in the CSV than there are 'tables'
 in the json.
"""

import sys
import os
import logging


# Needed to make relative package imports when running this file as a script
# (i.e. for testing purposes).
# Read why here: https://www.blog.pythonlibrary.org/2016/03/01/python-101-all
# -about-imports/

PYTHON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           os.pardir))
sys.path.append(PYTHON_PATH)

from housinginsights.tools import dbtools

from housinginsights.ingestion import DataReader, ManifestReader
from housinginsights.ingestion import CSVWriter, DataReader
from housinginsights.ingestion import HISql, TableWritingError
from housinginsights.ingestion import functions as ingestionfunctions

# configuration: see /logs/example-logging.py for usage examples
logging_path = os.path.abspath(os.path.join(PYTHON_PATH, "logs"))
logging_filename = os.path.abspath(os.path.join(logging_path, "ingestion.log"))
logging.basicConfig(filename=logging_filename, level=logging.DEBUG)

# Pushes everything from the logger to the command line output as well.
logging.getLogger().addHandler(logging.StreamHandler())


class LoadData(object):

    def __init__(self, database_choice=None, meta_path=None,
                 manifest_path=None, keep_temp_files=True):
        """
        Initializes the class with optional arguments. The default behaviour 
        is to load the local database with data tracked from meta.json 
        and manifest.csv within the 'python/scripts' folder.
        
        :param database_choice: choice of 'local_database', 
        'docker_database', and 'remote_database'
        :param meta_path: the path of the meta.json to be used
        :param manifest_path: the path of the manifest_path.csv to be used
        :param keep_temp_files: if True, temp clean pipe-delimited files will be
        archived in the 'python/logs' folder
        """

        # load defaults if no arguments passed
        _scripts_path = os.path.abspath(os.path.join(PYTHON_PATH, 'scripts'))
        if database_choice is None:
            database_choice = 'local_database'
        if meta_path is None:
            meta_path = os.path.abspath(os.path.join(_scripts_path,
                                                     'meta.json'))
        if manifest_path is None:
            manifest_path = os.path.abspath(os.path.join(_scripts_path,
                                                         'manifest.csv'))
        self._keep_temp_files = keep_temp_files

        # load given meta.json and manifest.csv files into memory
        self.meta = ingestionfunctions.load_meta_data(meta_path)
        self.manifest = ManifestReader(manifest_path)

        # setup engine for database_choice
        self.engine = dbtools.get_database_engine(database_choice)

    def drop_tables(self):
        """
        Returns the outcome of dropping all the tables from the 
        database_choice and then rebuilding.
        """
        db_conn = self.engine.connect()
        return db_conn.execute(
            "DROP SCHEMA public CASCADE;CREATE SCHEMA public;")

    def load_all_data(self):
        """
        Using manifest.csv, meta.json, and respective cleaners, validate and
        process the data and then load all usable data into the database.
        """
        # TODO: should this be moved into the __init__ of ManifestReader? Do we
        # TODO: ever want to use ManifestReader if it has duplicate rows?
        if not self.manifest.has_unique_ids():
            raise ValueError('Manifest has duplicate unique_data_id!')

        # Iterate through each row in the manifest then clean and validate
        for manifest_row in self.manifest:
            # Note: Incompletely filled out rows in the manifest can break the
            # other code
            # TODO: figure out a way to flag this issue early in loading
            # TODO: of manifest

            # only clean and validate data files flagged for use in database
            if manifest_row['include_flag'] == 'use':
                logging.info("{}: preparing to load row {} from the manifest".
                             format(manifest_row['unique_data_id'],
                                    len(self.manifest)))

                self._process_data_file(manifest_row=manifest_row)

    def _process_data_file(self, manifest_row):
        """
        Processes the data file for the given manifest row.
        """
        # get the file object for the data
        csv_reader = DataReader(meta=self.meta,
                                manifest_row=manifest_row,
                                load_from="file")

        # get file path for storing clean PSV files
        temp_filepath = os.path.abspath(
            os.path.join(logging_path, 'temp_{}.psv'.format(
                manifest_row['unique_data_id'])))

        # validate and clean
        self._create_clean_psv(table_name=manifest_row['destination_table'],
                               manifest_row=manifest_row,
                               csv_reader=csv_reader,
                               temp_filepath=temp_filepath)

    def _get_cleaner(self, table_name, manifest_row):
        """
        Returns the custom cleaner class that is to be used to clean the 
        specific data for use in database.
        
        :param table_name: the table name for that data being processed
        :param manifest_row: the row representing the data being loaded
        :return: instance of custom cleaner class
        """
        cleaner_class_name = self.meta[table_name]['cleaner']
        return ingestionfunctions.get_cleaner_from_name(
            meta=self.meta,
            manifest_row=manifest_row,
            name=cleaner_class_name)

    def _get_meta_only_fields(self, table_name, data_fields):
        """
        Returns fields that exist in meta.json but not CSV so we can add 
        them to the row as it is cleaned and written to PSV file.
        
        :param table_name: the table name for the data being processed
        :param data_fields: the fields for the data being processed
        :return: additional fields as dict
        """
        meta_only_fields = {}
        for field in self.meta[table_name]['fields']:
            if field['source_name'] not in data_fields:
                # adds 'sql_name',None as key,value pairs in dict
                meta_only_fields[field['sql_name']] = None
        return meta_only_fields

    def _configure_db_interface(self, manifest_row, temp_filepath):
        """
        Returns an interface object for the sql database and the equivalent 
        manifest row in the database.
        
        :param manifest_row: a given row in the manifest
        :param temp_filepath: the file path where PSV will be saved
        :return: interface object and sql manifest row as a tuple
        """
        # check for database manifest - create it if it doesn't exist
        sql_manifest_exists = \
            ingestionfunctions.check_or_create_sql_manifest(engine=self.engine)
        logging.info("sql_manifest_exists: {}".format(sql_manifest_exists))

        # configure database interface object and get matching manifest row
        interface = HISql(meta=self.meta, manifest_row=manifest_row,
                          engine=self.engine, filename=temp_filepath)
        sql_manifest_row = interface.get_sql_manifest_row()

        return interface, sql_manifest_row

    def _create_clean_psv(self, table_name, manifest_row, csv_reader,
                          temp_filepath):
        """
        Cleans the data for the table name in the given manifest row, writes 
        the clean data to PSV file, and then passes on that information so 
        the database can be updated accordingly.
        """
        # get database interface and it's equivalent manifest row
        sql_interface, sql_manifest_row = self._configure_db_interface(
            manifest_row=manifest_row, temp_filepath=temp_filepath)

        cleaner = self._get_cleaner(table_name=table_name,
                                    manifest_row=manifest_row)
        csv_writer = CSVWriter(meta=self.meta,
                               manifest_row=manifest_row,
                               filename=temp_filepath)

        # clean the file and save the output to a local pipe-delimited file
        if csv_reader.should_file_be_loaded(
                sql_manifest_row=sql_manifest_row):
            print("  Cleaning...")
            meta_only_fields = self._get_meta_only_fields(
                table_name=table_name, data_fields=csv_reader.keys)
            for idx, data_row in enumerate(csv_reader):
                data_row.update(meta_only_fields)  # insert other field dict
                clean_data_row = cleaner.clean(data_row, idx)
                if clean_data_row is not None:
                    csv_writer.write(clean_data_row)

            csv_writer.close()

            # write the data to the database
            self._update_database(table_name=table_name,
                                  sql_interface=sql_interface)

            if not self._keep_temp_files:
                csv_writer.remove_file()

    def _update_database(self, table_name, sql_interface):
        """
        Load the clean PSV file into the database
        """
        print("  Loading...")

        # Decide whether to append or replace the table
        if self.meta[table_name]["replace_table"]:
            logging.info("  replacing existing table")
            sql_interface.drop_table()

        # Appends to table; if dropped, it recreates
        sql_interface.create_table_if_necessary()
        try:
            sql_interface.write_file_to_sql()
        except TableWritingError:
            # TODO: tell user total count of errors.
            # currently write_file_to_sql() just writes in log that file failed
            pass

if __name__ == '__main__':
    """
    Continue to honor command line feature after refactoring to encapsulate 
    the module as a class. 
    """

    # use real data as default
    scripts_path = os.path.abspath(os.path.join(PYTHON_PATH, 'scripts'))
    meta_path = os.path.abspath(os.path.join(scripts_path, 'meta.json'))
    manifest_path = os.path.abspath(os.path.join(scripts_path, 'manifest.csv'))

    if 'sample' in sys.argv:
        meta_path = os.path.abspath(os.path.join(scripts_path,
                                                 'meta_sample.json'))
        manifest_path = os.path.abspath(
            os.path.join(scripts_path, 'manifest_sample.csv'))

    # for case of more than one database choice default to the option with
    # the lowest risk if database is updated
    if 'docker' in sys.argv:
        database_choice = 'docker_database'
        loader = LoadData(database_choice=database_choice, meta_path=meta_path,
                          manifest_path=manifest_path, keep_temp_files=True)
    elif 'remote' in sys.argv:
        database_choice = 'remote_database'
        # Don't want sample data in the remote database
        meta_path = os.path.abspath(os.path.join(scripts_path, 'meta.json'))
        manifest_path = os.path.abspath(
            os.path.join(scripts_path, 'manifest.csv'))
        loader = LoadData(database_choice=database_choice, meta_path=meta_path,
                          manifest_path=manifest_path, keep_temp_files=True)
    else:
        database_choice = 'local_database'
        loader = LoadData(database_choice=database_choice, meta_path=meta_path,
                          manifest_path=manifest_path, keep_temp_files=True)

    if 'rebuild' in sys.argv:
        loader.drop_tables()

    loader.load_all_data()
