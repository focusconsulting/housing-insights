import sys
import os
import logging
import json
import csv


#Needed to make relative package imports when running this file as a script (i.e. for testing purposes).
#Read why here: https://www.blog.pythonlibrary.org/2016/03/01/python-101-all-about-imports/
if __name__ == '__main__':
    import sys, os
    sys.path.append(os.path.abspath('../'))

from housinginsights.ingestion.DataReader import DataReader
from housinginsights.tools import dbtools

from housinginsights.ingestion import DataReader, ManifestReader
from housinginsights.ingestion import CSVWriter, DataReader
from housinginsights.ingestion import HISql, TableWritingError
from housinginsights.ingestion import ACSRentCleaner, GenericCleaner
from housinginsights.ingestion import BuildingCleaner
from housinginsights.ingestion import load_meta_data, check_or_create_sql_manifest
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


def main(database_choice):
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
    # Check if local database is running
    if database_choice == "docker_database":
        try:
            is_local_db_running = dbtools.check_for_docker_database()
            if not is_local_db_running:
                dbtools.start_local_database_server()
                # Load manifest data into a table.
                dbtools.create_manifest_table('manifest_sample.csv')
        except Exception as e:
            print("Could not start postgres database is docker running?")

    meta = load_meta_data('meta_sample.json')
    engine = dbtools.get_database_engine(database_choice)
    manifest = ManifestReader('manifest_sample.csv')

    sql_manifest_exists = check_or_create_sql_manifest(engine=engine)
    print("sql_manifest_exists: {}".format(sql_manifest_exists))

    #TODO should this be moved into the __init__ of ManifestReader? Do we ever want to use ManifestReader if it has duplicate rows?
    if not manifest.has_unique_ids():
        raise ValueError('Manifest has duplicate unique_data_id!')

    for manifest_row in manifest:
        logging.info("Preparing to load row {} from the manifest".format(len(manifest)))

        
        csv_reader = DataReader(meta = meta, manifest_row=manifest_row)
        csv_writer = CSVWriter(meta = meta, manifest_row = manifest_row)
        sql_interface = HISql(meta = meta, manifest_row = manifest_row, engine = engine)
        sql_manifest_row = sql_interface.get_sql_manifest_row()

        #Assign an appropriate testing cleaner
        #TODO need more robust way to do this long term. get_cleaner function?
        if manifest_row['destination_table'] == "acs_rent_median_temp":
            cleaner = ACSRentCleaner(meta, manifest_row)
        else:
            cleaner = BuildingCleaner(meta, manifest_row)

        #clean the file and save the output to a local pipe-delimited file
        if csv_reader.should_file_be_loaded(sql_manifest_row=sql_manifest_row):
            print("  Ready to clean {}".format(csv_reader.destination_table))
            for idx, data_row in enumerate(csv_reader):
                clean_data_row = cleaner.clean(data_row, idx)
                if clean_data_row != None:
                    csv_writer.write(clean_data_row)

            csv_writer.close()
            print("  Ready to load")
            
            #Uncomment this to drop instead of append. 
            #TODO add parameter to handle dropping data vs. appending. Should work w/ manifest.
            sql_interface.drop_table()
            
            sql_interface.create_table()
            try:
                sql_interface.write_file_to_sql()
            except TableWritingError:
                #keep loading other files.
                #TODO handle logging of missed files better - write_... function just writes in log
                pass
            #TODO add/update the appropriate row to the SQL manifest table indicating new status

if __name__ == '__main__':

    #the appropriate database name in secrets.json.
    #TODO make this changeable via sys.argv
    database_choice = 'local_database'

    if 'rebuild' in sys.argv:
        drop_tables(database_choice)

    main(database_choice)
