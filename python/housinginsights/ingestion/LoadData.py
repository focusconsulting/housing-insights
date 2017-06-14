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
import argparse
import json
from datetime import datetime
from csv import DictWriter
from sqlalchemy import Table, Column, Integer, String, MetaData

# Needed to make relative package imports when running this file as a script
# (i.e. for testing purposes).
# Read why here: https://www.blog.pythonlibrary.org/2016/03/01/python-101-all
# -about-imports/

PYTHON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           os.pardir, os.pardir))

logging_path = os.path.abspath(os.path.join(PYTHON_PATH, "logs"))
logging_filename = os.path.abspath(os.path.join(logging_path, "ingestion.log"))

#append to path if running this file directly, otherwise assume it's already been appended. 
if __name__ == "__main__":
    sys.path.append(PYTHON_PATH)

from housinginsights.tools import dbtools

from housinginsights.ingestion import CSVWriter, DataReader
from housinginsights.ingestion import HISql, TableWritingError
from housinginsights.ingestion import functions as ingestionfunctions
from housinginsights.ingestion.Manifest import Manifest


class LoadData(object):

    def __init__(self, database_choice=None, meta_path=None,
                 manifest_path=None, keep_temp_files=True, drop_tables=False):
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
            self.database_choice = 'docker_database'
        else:
            self.database_choice = database_choice
        if meta_path is None:
            meta_path = os.path.abspath(os.path.join(_scripts_path,
                                                     'meta.json'))
        if manifest_path is None:
            manifest_path = os.path.abspath(os.path.join(_scripts_path,
                                                         'manifest.csv'))
        self._keep_temp_files = keep_temp_files

        # load given meta.json and manifest.csv files into memory
        self.meta = ingestionfunctions.load_meta_data(meta_path)
        self.manifest = Manifest(manifest_path)

        # setup engine for database_choice
        self.engine = dbtools.get_database_engine(self.database_choice)

        # write the meta.json to the database
        self._meta_json_to_database()

        self._failed_table_count = 0

        self.drop_tables = drop_tables

    def _drop_tables(self):
        """
        Returns the outcome of dropping all the tables from the 
        database_choice and then rebuilding.
        """
        logging.info("Dropping all tables from the database!")
        db_conn = self.engine.connect()
        query_result = list()
        query_result.append(db_conn.execute(
            "DROP SCHEMA public CASCADE;CREATE SCHEMA public;"))

        if self.database_choice == 'remote_database' or self.database_choice \
                == 'remote_database_master':
            query_result.append(db_conn.execute('''
            GRANT ALL PRIVILEGES ON SCHEMA public TO housingcrud;
            GRANT ALL PRIVILEGES ON ALL TABLES    IN SCHEMA public TO housingcrud;
            GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO housingcrud;
            GRANT ALL ON SCHEMA public TO public;
            '''))
        return query_result

    def _meta_json_to_database(self):
        """
        Makes sure we have a meta table in the database.
        If not, it creates it with appropriate fields.
        """

        sqlalchemy_metadata = MetaData()  # this is unrelated to our meta.json
        meta_table = Table('meta', sqlalchemy_metadata,
                           Column('meta', String))

        sqlalchemy_metadata.create_all(self.engine)
        json_string = json.dumps(self.meta)
        ins = meta_table.insert().values(meta=json_string)
        conn = self.engine.connect()
        conn.execute("DELETE FROM meta;")
        conn.execute(ins)

    def _remove_existing_data(self, uid, manifest_row):
        """
        Removes all rows in the respective table for the given unique_data_id
        then sets status = deleted for the unique_data_id in the
        database manifest.

        :param uid: unique_data_id for the data to be updated
        :param manifest_row: the row for uid in the manifest
        :return: result from executing delete query as
        sqlalchemy result object if row exists in sql manifest - else
        returns None
        """
        temp_filepath = self._get_temp_filepath(
            manifest_row=manifest_row)

        # get objects for interfacing with the database
        sql_interface = self._configure_db_interface(
            manifest_row=manifest_row, temp_filepath=temp_filepath)
        sql_manifest_row = sql_interface.get_sql_manifest_row()

        try:
            # delete only rows with data_id in respective table
            table_name = sql_manifest_row['destination_table']
            query = "DELETE FROM {} WHERE unique_data_id =" \
                    " '{}'".format(table_name, uid)
            logging.info("\t\tDeleting {} data from {}!".format(
                uid, table_name))
            result = self.engine.execute(query)

            # change status = deleted in sql_manifest
            logging.info("\t\tResetting status in sql manifest row!")
            sql_interface.update_manifest_row(conn=self.engine,
                                              status='deleted')

            return result
        except TypeError:
            logging.info("\t\tNo sql_manifest exists! Proceed with adding"
                         " new data to the database!")

        return None

    def _get_most_recent_timestamp_subfolder(self, root_folder_path):
        """
        Returns the most recent timestamp subfolder in a given folder path.

        :param root_folder_path: the path for the directory containing
        timestamp subfolders
        :type root_folder_path: str

        :return: most recent timestamp subfolder
        :type: str
        """
        walk_gen = os.walk(root_folder_path)
        root, dirs, files = walk_gen.__next__()
        dirs.sort(reverse=True)
        return dirs[0]

    def make_manifest(self, all_folders_path):
        """
        Creates a new manifest.csv with updated data date and filepath for
        the raw data files within the most recent timestamp subfolder of the
        given folder path.

        A new instance of manifest object is created from the new
        manifest.csv file.

        :param all_folders_path: the folder that contains the timestamped
        subfolders representing updated raw data files that should be loaded
        into the database
        :type all_folders_path: str

        :param overwrite: should the current manifest.csv be overwritten?
        :type overwrite: bool

        :return: the path of the manifest
        """
        # get most recent subfolder, gather info for updating manifest
        timestamp = self._get_most_recent_timestamp_subfolder(
            all_folders_path)
        most_recent_subfolder_path = os.path.join(all_folders_path,
                                                  timestamp)

        return self.manifest.update_manifest(most_recent_subfolder_path)

    def update_database(self, unique_data_id_list):
        """
        Reloads only the flat file associated to the unique_data_id in
        unique_data_id_list.

        Returns a list of unique_data_ids that were successfully updated.
        """
        logging.info("update_only(): attempting to update {} data".format(
            unique_data_id_list))
        processed_data_ids = []

        for uid in unique_data_id_list:
            manifest_row = self.manifest.get_manifest_row(uid)

            # process manifest row for requested data_id if flagged for use
            if manifest_row is None:
                logging.info("\tSkipping: {} not found in manifest!".format(
                    uid))
            else:
                logging.info("\tManifest row found for {} - preparing to "
                             "remove data.".format(uid))
                self._remove_existing_data(uid=uid, manifest_row=manifest_row)

                # follow normal workflow and load data_id
                logging.info(
                    "\tLoading {} data!".format(uid))
                self._process_data_file(manifest_row=manifest_row)
                processed_data_ids.append(uid)

        return processed_data_ids

    def _get_temp_filepath(self, manifest_row):
        """
        Returns a file path where intermediary clean psv file will be saved.
        """
        return os.path.abspath(
                    os.path.join(logging_path, 'temp_{}.psv'.format(
                        manifest_row['unique_data_id'])))

    def rebuild(self):
        """
        Using manifest.csv, meta.json, and respective cleaners, validate and
        process the data and then load all usable data into the database
        after dropping all tables.
        """
        if self.drop_tables:
            self._drop_tables()

        # reload meta.json into db
        self._meta_json_to_database()

        processed_data_ids = []

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

            processed_data_ids.append(manifest_row['unique_data_id'])

        return processed_data_ids

    def _process_data_file(self, manifest_row):
        """
        Processes the data file for the given manifest row.
        """
        # get the file object for the data
        csv_reader = DataReader(meta=self.meta,
                                manifest_row=manifest_row,
                                load_from="file")

        # get file path for storing clean PSV files
        temp_filepath = self._get_temp_filepath(manifest_row=manifest_row)

        # validate and clean
        self._load_single_file(table_name=manifest_row['destination_table'],
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
        Returns an interface object for the sql database
        
        :param manifest_row: a given row in the manifest
        :param temp_filepath: the file path where PSV will be saved
        """
        # check for database manifest - create it if it doesn't exist
        sql_manifest_exists = \
            ingestionfunctions.check_or_create_sql_manifest(engine=self.engine)
        logging.info("sql_manifest_exists: {}".format(sql_manifest_exists))

        # configure database interface object and get matching manifest row
        interface = HISql(meta=self.meta, manifest_row=manifest_row,
                          engine=self.engine, filename=temp_filepath)
        return interface

    def _load_single_file(self, table_name, manifest_row, csv_reader,
                          temp_filepath):
        """
        Cleans the data for the table name in the given manifest row, writes 
        the clean data to PSV file, and then passes on that information so 
        the database can be updated accordingly.
        """
        # get database interface and it's equivalent manifest row
        sql_interface = self._configure_db_interface(
            manifest_row=manifest_row, temp_filepath=temp_filepath)

        sql_manifest_row = sql_interface.get_sql_manifest_row()

        cleaner = self._get_cleaner(table_name=table_name,
                                    manifest_row=manifest_row)
        csv_writer = CSVWriter(meta=self.meta,
                               manifest_row=manifest_row,
                               filename=temp_filepath)

        # clean the file and save the output to a local pipe-delimited file
        # if it doesn't have a 'loaded' status in the database manifest
        if csv_reader.should_file_be_loaded(sql_manifest_row=sql_manifest_row):
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
            self._update_database(sql_interface=sql_interface)

            if not self._keep_temp_files:
                csv_writer.remove_file()

    def _update_database(self, sql_interface):
        """
        Load the clean PSV file into the database
        """
        print("  Loading...")

        # create table if it doesn't exist
        sql_interface.create_table_if_necessary()
        try:
            sql_interface.write_file_to_sql()
        except TableWritingError:
            # TODO: tell user total count of errors.
            # currently write_file_to_sql() just writes in log that file failed
            self._failed_table_count += 1
            pass


def main(passed_arguments):
    """
    Initializes load procedure based on passed command line arguments and
    options.
    """

    # use real data as default
    scripts_path = os.path.abspath(os.path.join(PYTHON_PATH, 'scripts'))
    meta_path = os.path.abspath(os.path.join(scripts_path, 'meta.json'))
    manifest_path = os.path.abspath(os.path.join(scripts_path, 'manifest.csv'))

    #Locally, we can optionally have sample data
    if passed_arguments.sample and passed_arguments.database != 'remote':
        meta_path = os.path.abspath(os.path.join(scripts_path,
                                                 'meta_sample.json'))
        manifest_path = os.path.abspath(
            os.path.join(scripts_path, 'manifest_sample.csv'))

    # for case of more than one database choice default to the option with
    # the lowest risk if database is updated
    if passed_arguments.database == 'docker':
        database_choice = 'docker_database'
        drop_tables = True

    elif passed_arguments.database == 'docker_local':
        database_choice = 'docker_with_local_python'
        drop_tables = True

    elif passed_arguments.database == 'remote':
        database_choice = 'remote_database'
        drop_tables = False #TODO this is a hacky way to avoid dropping tables because it's not working with RDS...

        # Only users with additional admin privileges can rebuild the
        # remote database
        if not passed_arguments.update_only:
            database_choice = 'remote_database_master'

    # TODO: do we want to default to local or docker?
    elif passed_arguments.database == 'local':
        database_choice = 'local_database'
        drop_tables = True



    #universal defaults
    keep_temp_files = True


    #Instantiate and run the loader
    loader = LoadData(database_choice=database_choice, meta_path=meta_path,
                      manifest_path=manifest_path, keep_temp_files=keep_temp_files,
                      drop_tables=drop_tables)

    if passed_arguments.update_only:
        loader.update_database(passed_arguments.update_only)
    else:
        loader.rebuild()



    #TODO add in failures report here e.g. _failed_table_count

if __name__ == '__main__':
    """
    Continue to honor command line feature after refactoring to encapsulate 
    the module as a class. 
    """

    # configuration: see /logs/example-logging.py for usage examples
    logging.basicConfig(filename=logging_filename, level=logging.DEBUG)
    # Pushes everything from the logger to the command line output as well.
    logging.getLogger().addHandler(logging.StreamHandler())


    description = 'Loads our flat file data into the database of choice. You ' \
                  'can load sample or real data and/or rebuild or update only '\
                  'specific flat files based on unique_data_id values.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("database", help='which database the data should be '
                                         'loaded to',
                        choices=['docker', 'docker-local', 'local', 'remote'])
    parser.add_argument('-s', '--sample', help='load with sample data',
                        action='store_true')
    parser.add_argument('--update-only', nargs='+',
                        help='only update tables with these unique_data_id '
                             'values')

    # handle passed arguments and options
    main(parser.parse_args())
