##########################################################################
## Summary
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

##########################################################################
## Imports & Configuration
##########################################################################
#external imports
import logging
import json
import pandas as pandas
import csv
from urllib.request import urlretrieve

#project imports
import database_management

#configuration
#See /logs/example-logging.py for usage examples
logging_filename = "../logs/ingestion.log"
logging.basicConfig(filename=logging_filename, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())     #Pushes everything from the logger to the command line output as well.




#############################
#CONSTANTS
#############################

constants = {
    'manifest_filename': 'manifest.csv',
}



#############################
#FUNCTIONS
#############################

def do_fields_match(csv_data, manifest):
    '''
    csv_data = the memory version of the csv file, either a pandas dataframe or other object depending on our read csv approach
    manifest = the memory version of manifest.json that can be traversed as a nested dictionary.

    Checks that all fields are the same as expected,
    If so, returns true. if not it raises an exception.
    '''
    pass

def should_file_be_loaded(manifest_row, sql_manifest_table):
    '''
    If the sql_manifest_table indicates that this file is already loaded into this copy of the database, returns False
    Check the manifest.csv to decide if it should be loaded (currently called the 'skip' column in manifest.csv)

    '''
    pass

def get_sql_manifest_table(engine, manifest_filename = constants['manifest_filename']):
    '''
    Loads the table 'manifest' from sql. engine is the activated sqlAlchemy engine to be used.
    The 'manifest' table is a duplicate of the 'manifest.csv' file, but it reflects the current status of the database.
    Returns the sql_manifest_table, which is a memory representation of the table - probably a Pandas dataframe.
    '''
    sql_manifest_table = None
    return sql_manifest_table


def update_sql_manifest(status = None, engine):
    '''
    If the 'manifest' table does not exist in SQL, create it.
        -in SQL, the manifest table has the exact same data as manifest.csv, but one additional column called 'status'
         should be added, which reflects whether that file has been loaded into the database or not.
    Call this function twice for every row of the database:
        -immediately before loading a new file into the database, the 'status' column should be "started"
        -immediately after loading is complete, 'status' column should be 'loaded'

        -if the file loading encounters an error, call this function and set the 'status' column to 'error'
    '''
    pass

def download_csv_file(manifest_row):
    '''
    Checks to see if the file already exists locally.
    If it doesn't exist, it downloads it from s3.
    raises exception if the file does not exist and can't be downloaded for some reason.
    Be careful about leading/trailing '/' in the manifest.csv - should probably be able to handle with and without so that less user knowledge is required when adding files to the manifest.csv
    '''
    pass


def csv_to_sql(manifest_row, engine, meta):
    """
    Does the actual loading of the file into SQL. This assumes all necessary tests have been passed (i.e. do_fields_match etc.)
    Dont use pandas_dataframe.to_sql() method because this is super slow.

    We do want to load the CSV into memory, so that Python can apply data cleaning functions
    Look into numpy arrays as an option?
    If the table doesnt exist, create it (probably using a CREATE TABLE sql query plus a for loop that creates
    the necessary add column X as datatype list of SQL queries)
    If the table already exists, it should be appended to.
    Should use meta (which is already loaded into memory from meta.json) to parse data types appropriately
    Date parsing will be tricky - needs to be able to handle multiple formats. If necessary, we could add another attribute to the meta.json
    e.g.:  date_format: YYYY-MM-DD THH:MM:SS, which can be in whatever format the date parser needs


    first version: loads data by converting to the data type listed in meta. raises error if a data inconsistency is found (e.g. a string
                   in a field that should be integer) and refuses to import the whole table. Specific error message / field is added to the log.
                   main() should have a way of handling the raised error by adding error to the manifest.status in SQL for this row, and moving on
                   to the next file in the manifest.
    second version: calls a set of custom cleaning functions based on the table_name, to handle data quality issues we are currently identifying on Github.
                    Idea: use a dictionary like this: {table_name: cleaning_function()} to tell it what cleaning_function to apply.
                    Probably want to put the cleaning functions into a separate file

    """
    pass

def drop_tables(database_choice):
    '''
    used to rebuild the database by first dropping all tables before running main()
    '''
    connect_str = database_management.get_connect_str(database_choice)
    engine = database_management.create_engine(connect_str)
    database_connection = engine.connect()
    query_result = database_connection.execute("DROP SCHEMA public CASCADE;CREATE SCHEMA public;")

def main(database_choice):

    '''
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
    '''

    #setup
    sql_manifest_table = get_sql_manifest_table()
    meta = load_meta_data()

    #Run checks:
    should_file_be_loaded()
    do_fields_match()

    #Load the table into SQL
    download_csv_file()  #does nothing if the file already exists locally, otherwise it downloads it.
    csv_to_sql()




if __name__ == '__main__':

    database_choice = 'local_database' #the appropriate database name in secrets.json. Should make this changeable via optional positional sys.argv

    if 'rebuild' in sys.argv
        drop_tables(database_choice)

    main(database_choice)
