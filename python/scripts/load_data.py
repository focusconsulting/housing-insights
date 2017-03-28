import sys
import os
import logging
import json
import csv


#Needed to make relative package imports when running this file as a script (i.e. for testing purposes).
#Read why here: https://www.blog.pythonlibrary.org/2016/03/01/python-101-all-about-imports/

import sys, os
sys.path.append(os.path.abspath('../'))

from housinginsights.ingestion.DataReader import DataReader
from housinginsights.tools import dbtools

from housinginsights.ingestion import DataReader, ManifestReader
from housinginsights.ingestion import CSVWriter, DataReader
from housinginsights.ingestion import HISql, TableWritingError
from housinginsights.ingestion import functions as ingestionfunctions

##########################################################################
# Summary
##########################################################################

'''
Loads our flat file data into the Postgres database

Notes:
 - manifest.csv has every flat file that needs to be loaded (i.e. CSV's we have downloaded).
 - other scripts can get data that is available from APIs, so manifest won't reflect all the data we are including
 - meta.json provides meta information about our *SQL* tables. Note that because multiple CSV's can go into the same table
   (i.e. two different versions of the same data), there will be more rows in the CSV than there are 'tables' in the json.

'''

# configuration
# See /logs/example-logging.py for usage examples
logging_filename = "../logs/ingestion.log"
logging_path = os.path.abspath("../logs")
logging.basicConfig(filename=logging_filename, level=logging.DEBUG)

# Pushes everything from the logger to the command line output as well.
logging.getLogger().addHandler(logging.StreamHandler())


#############################
# FUNCTIONS
#############################


# complete, tests not written
def drop_tables(database_choice):
    """
    used to rebuild the database by first dropping all tables before running main()
    """
    engine = dbtools.get_database_engine(database_choice)
    db_conn = engine.connect()
    query_result = db_conn.execute("DROP SCHEMA public CASCADE;CREATE SCHEMA public;")


def main(database_choice, meta_path, manifest_path, keep_temp_files = True):
    """
    Main routine, calls all the other ones in this file as needed.

    Big picture:
        - Use manifest.csv to find out all the files we want to load
        - Compare current manifest.csv to the sql database manifest table, which reflects manifest.csv as
          of the last time this script was run, and tells us whether or not the file has already been loaded in this database.
        - Use meta.json to make sure the CSV file has all the fields we expect it to, and to decide the data type of each field
        - Load the csv into the database

    If there is an error loading a file (either flagged error from fields not matching, or parsing error if data type isn't right):
    - skip loading this file,
    - report the error to SQL using update_sql_manifest(status="error")
    - use logging.warning() to write the specific error encountered to the log file
    - at the end of loading print an error message to the console
    """
    meta = ingestionfunctions.load_meta_data(meta_path)
    engine = dbtools.get_database_engine(database_choice)
    manifest = ManifestReader(manifest_path)

    sql_manifest_exists = ingestionfunctions.check_or_create_sql_manifest(engine=engine)
    logging.info("sql_manifest_exists: {}".format(sql_manifest_exists))

    #TODO should this be moved into the __init__ of ManifestReader? Do we ever want to use ManifestReader if it has duplicate rows?
    if not manifest.has_unique_ids():
        raise ValueError('Manifest has duplicate unique_data_id!')

    for manifest_row in manifest:
        #Incompletely filled out rows in the manifest can break the other code
        if manifest_row['include_flag'] == 'use':
            logging.info("{}: preparing to load row {} from the manifest".format(manifest_row['unique_data_id'],len(manifest)))

            temp_filepath = os.path.abspath(
                                os.path.join(
                                    logging_path,
                                    'temp_{}.psv'.format(manifest_row['unique_data_id'])
                                ))
            csv_reader = DataReader(meta = meta, manifest_row=manifest_row, load_from="file")
            csv_writer = CSVWriter(meta = meta, manifest_row = manifest_row, filename = temp_filepath)
            sql_interface = HISql(meta = meta, manifest_row = manifest_row, engine = engine, filename=temp_filepath)
            sql_manifest_row = sql_interface.get_sql_manifest_row()

            #Assign an appropriate testing cleaner
            tablename = manifest_row['destination_table']
            cleaner_class_name = meta[tablename]['cleaner']
            cleaner = ingestionfunctions.get_cleaner_from_name(
                                        meta=meta, 
                                        manifest_row=manifest_row, 
                                        name= cleaner_class_name)

            #clean the file and save the output to a local pipe-delimited file
            if csv_reader.should_file_be_loaded(sql_manifest_row=sql_manifest_row):
                print("  Ready to clean {}".format(csv_reader.destination_table))
                for idx, data_row in enumerate(csv_reader):
                    clean_data_row = cleaner.clean(data_row, idx)
                    if clean_data_row != None:
                        csv_writer.write(clean_data_row)

                csv_writer.close()
                print("  Ready to load")
                
                #Decide whether to append or replace the table
                if meta[tablename]["replace_table"] == True:
                    logging.info("  replacing existing table")
                    sql_interface.drop_table()
                
                #Appends to table; if dropped, it recreates
                sql_interface.create_table()
                try:
                    sql_interface.write_file_to_sql()
                except TableWritingError:
                    #TODO tell user total count of errors. 
                    #currently write_file_to_sql() just writes in log that file failed
                    pass
                if keep_temp_files == False:
                    csv_writer.remove_file()

if __name__ == '__main__':


    #local, real data is the default
    database_choice = 'local_database'
    meta_path = 'meta.json'
    manifest_path = 'manifest.csv'
    
    if 'sample' in sys.argv:
        meta_path = 'meta_sample.json'
        manifest_path = 'manifest_sample.csv'

    if 'docker' in sys.argv:
        database_choice = 'docker_database'



    if 'remote' in sys.argv:
        database_choice = 'remote_database'
        #Don't want sample data in the remote database
        meta_path = 'meta.json'
        manifest_path = 'manifest.csv'


    if 'rebuild' in sys.argv:
        drop_tables(database_choice)

    main(database_choice, meta_path, manifest_path, keep_temp_files = True)
