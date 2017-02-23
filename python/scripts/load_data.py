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

from housinginsights.ingestion.DataReader import DataReader, ManifestReader


##########################################################################
# Summary
##########################################################################

'''
Loads our flat file data into the Postgres database
'''

'''
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

# Completed, tests not written.
def load_meta_data(filename='meta.json'):
    """
    Expected meta data format:
        { tablename: {fields:[
            {   "display_name": "Preservation Catalog ID",
                "display_text": "description of what this field is",
                "source_name": "Nlihc_id",
                "sql_name": "nlihc_id",
                "type": "object"
            }
            ]}
        }
    """
    with open(filename) as fh:
        meta = json.load(fh)

    json_is_valid = True
    try:
        for table in meta:
            for field in meta[table]['fields']:
                for key in field:
                    if key not in ('display_name', 'display_text', 'source_name', 'sql_name', 'type'):
                        json_is_valid = False
                        first_json_error = "Location: table: {}, section: {}, attribute: {}".format(table, field, key)
                        raise ValueError("Error found in JSON, check expected format. {}".format(first_json_error))
    except:
        raise ValueError("Error found in JSON, check expected format.")

    logging.info("{} imported. JSON format is valid: {}".format(filename, json_is_valid))

    return meta



# Completed, tests incomplete
def get_sql_manifest_row(database_connection, csv_row):
    """
    Loads the row from the manifest table that matches the unique_data_id in csv_row.
    Returns the manifest_row as a dictionary, or None if no matching database row was found
    """

    unique_data_id = csv_row['unique_data_id']
    sql_query = "SELECT * FROM manifest WHERE unique_data_id = '{}'".format(unique_data_id)

    # temp
    # sql_query = "SELECT * FROM manifest WHERE unique_data_id = '{}'".format('my_data_id')
    logging.info("  Getting SQL manifest row for {} using query {}".format(unique_data_id,sql_query))
    query_result = database_connection.execute(sql_query)

    # convert the sqlAlchemy ResultProxy object into a list of dictionaries
    results = [dict(row.items()) for row in query_result]

    # We expect there to be exactly one row matching the query if the csv_row is already in the database
    if len(results) > 1:
        raise ValueError('Found multiple rows in database for data id {}'.format(unique_data_id))

    # Return just the dictionary of results, not the list of dictionaries
    if len(results) == 1:
        return results[0]

    if len(results) == 0:
        return None







# complete, tests not written
def drop_tables(database_choice):
    """
    used to rebuild the database by first dropping all tables before running main()
    """
    connect_str = dbtools.get_connect_str(database_choice)
    engine = dbtools.create_engine(connect_str)
    database_connection = engine.connect()
    query_result = database_connection.execute("DROP SCHEMA public CASCADE;CREATE SCHEMA public;")


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
    try:
        is_local_db_running = dbtools.check_for_local_database()
        if not is_local_db_running:
            dbtools.start_local_database_server()
            # Load manifest data into a table.
            dbtools.create_manifest_table('manifest_sample.csv')
    except Exception as e:
        print("Could not start postgres database is docker running?")

    meta = load_meta_data('meta_sample.json')
    database_connection = dbtools.get_database_connection(database_choice)

    manifest = ManifestReader('manifest_sample.csv')

    if not manifest.has_unique_ids(): 
        raise ValueError('Manifest has duplicate unique_data_id!')

    for manifest_row in manifest:
        logging.info("Preparing to load row {} from the manifest".format(len(manifest)))

        sql_manifest_row = get_sql_manifest_row(database_connection=database_connection, csv_row=manifest_row)
        csv_reader = DataReader(manifest_row=manifest_row)
        
        if csv_reader.should_file_be_loaded(sql_manifest_row=sql_manifest_row):
            if csv_reader.do_fields_match(meta):
                
                print("  Ready to clean {}".format(csv_reader.destination_table))
                for data_row in csv_reader:
                    #clean rows and add them to cleaned.csv
                    pass
                    #TODO normalize the date functions for all date field types
                    #TODO apply cleaning functions specific to this data file
                    #TODO write the row to a temporary cleaned.csv file

                print("  Ready to load")
                
                #TODO write the cleaned.csv to the appropriate SQL table
                #TODO add/update the appropriate row to the SQL manifest table indicating new status
                pass




if __name__ == '__main__':

    #the appropriate database name in secrets.json.
    #TODO make this changeable via sys.argv
    database_choice = 'local_database' 

    if 'rebuild' in sys.argv:
        drop_tables(database_choice)

    main(database_choice)




