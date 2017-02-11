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

##########################################################################
# Imports & Configuration
##########################################################################
# external imports
import logging
import json
import csv
from urllib.request import urlretrieve

# Needed to make relative package imports when running this file as a script (i.e. for testing purposes). Read why here:
# https://www.blog.pythonlibrary.org/2016/03/01/python-101-all-about-imports/
if __name__ == '__main__':
    import sys, os
    sys.path.append(os.path.abspath('../../'))

# Relative package imports
from housinginsights.tools import database

# configuration
# See /logs/example-logging.py for usage examples
logging_filename = "../../logs/ingestion.log"
logging.basicConfig(filename=logging_filename, level=logging.DEBUG)

# Pushes everything from the logger to the command line output as well.
logging.getLogger().addHandler(logging.StreamHandler())


#############################
# FUNCTIONS
#############################

# Completed, tests created.
def do_fields_match(data_row, meta, table_name):
    '''
    data_row = a dictionary representing one row of data, with the dict keys as header names
    meta = the full meta.json. 

    Checks that all fields are the same as expected,
    If so, returns true. if not it raises an exception.
    '''
    field_list = meta[table_name]['fields']
    included = {}

    # Initialize values - start out assuming all is OK until we identify problems.
    return_value = True
    not_found = []

    # Check that all of the data columns are in the meta.json
    for field in data_row:
        if not any(d.get('source_name', None) == field for d in field_list):
            not_found.append('"{}" in CSV not found in meta'.format(field))
            return_value = False

    # Check that all the meta.json columns are in the data
    for field in field_list:
        if field['source_name'] not in data_row:
            not_found.append('"{}" in meta.json not found in data'.format(field['source_name']))
            return_value = False

    # Log our errors if any
    if return_value == False:
        logging.warning("do_fields_match: {}. '{}' had missing items:\n{}".format(return_value, table_name, not_found))
    else:
        logging.info("do_fields_match: {}. meta.json and csv field lists match completely for '{}'".format(return_value, table_name))

    return return_value


# Completed, tests not written.
def load_meta_data(filename='meta.json'):
    '''
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
    '''
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


# Completed, tests not written
def read_csv_manifest(filename = 'manifest.csv'):
    '''
    Reads each line of the csv manifest, which specifies which files should be loaded

    TODO consider switching this to use the same DataReader class that is being developed for reading from SQL?
    '''
    with open(filename, 'rU') as data:
        reader = csv.DictReader(data)
        for row in reader:
            yield row


# Completed, test created
def check_csv_manifest_unique_ids(filename = 'manifest.csv'):
    '''
    Makes sure that every value in the manifest column 'unique_data_id' is in fact unique. 
    This makes sure that we can rely on this column to uniquely identify a source CSV file,
    and and can connect a record in the SQL manifest to the manifest.csv
    '''
    unique_ids = {}

    for row in read_csv_manifest(filename):
        if row['unique_data_id'] in unique_ids:
            return False
        else:
            unique_ids[row['unique_data_id']] = 'found'

    return True


# Completed, tests incomplete
def get_sql_manifest_row(database_connection, csv_row):
    '''
    Loads the row from the manifest table that matches the unique_data_id in csv_row.
    Returns the manifest_row as a dictionary, or None if no matching database row was found
    '''

    unique_data_id = csv_row['unique_data_id']
    sql_query = "SELECT * FROM manifest WHERE unique_data_id = '{}'".format(unique_data_id)

    # temp
    # sql_query = "SELECT * FROM manifest WHERE unique_data_id = '{}'".format('my_data_id')
    logging.info(sql_query)
    query_result = database_connection.execute(sql_query)

    # convert the sqlAlchemy ResultProxy object into a list of dictionaries
    results = [dict(row.items()) for row in query_result]

    # We expect there to be exactly one row matching the query if the csv_row is already in the database
    if len(results)>1:
        raise ValueError('Found multiple rows in database for data id {}'.format(unique_data_id))

    # Return just the dictionary of results, not the list of dictionaries
    if len(results)==1:
        return results[0]

    if len(results)==0:
        return None


# incomplete
def update_sql_manifest(database_connection, status = None):
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


# complete, tests not written
def should_file_be_loaded(csv_row, sql_row):
    '''
    If the sql_manifest_table indicates that this file is already loaded into this copy of the database, returns False
    Check the manifest.csv to decide if it should be loaded (currently called the 'skip' column in manifest.csv)

    '''
    if csv_row['include_flag'] == 'use':
        if sql_row == None:
            return True
        if sql_row['include_flag'] != 'loaded':
            return True
        if sql_row['include_flag'] == 'loaded':
            logging.info("{} is already in the database, skipping".format(csv_row['unique_data_id']))
            return False
    else:
        logging.info("{} include_flag is {}, skipping".format(csv_row['unique_data_id'], csv_row['include_flag']))
        return False


# complete, tests not written
def download_data_file(csv_row):
    '''
    Checks to see if the file already exists locally.
    If it doesn't exist, it downloads it from s3.
    raises exception if the file does not exist and can't be downloaded for some reason.
    Be careful about leading/trailing '/' in the manifest.csv - should probably be able to handle with and without so that less user knowledge is required when adding files to the manifest.csv
    '''
    from urllib.request import urlretrieve

    # TODO make sure that both of these can handle trailing/leading slashes appropriately
    local_path = os.path.join(os.path.dirname(__file__), csv_row['local_folder'], csv_row['filepath'])
    s3_path = csv_row['s3_folder'] + csv_row['filepath']

    try:
        with open(local_path) as f:
            myreader=csv.reader(f,delimiter=',')
            headers = next(myreader)

    except FileNotFoundError as e:
        logging.info("  file not found. attempting to download file to disk: " + s3_path)
        urlretrieve(s3_path,local_path)
        logging.info("  download complete.")
        with open(local_path) as f:
            myreader=csv.reader(f,delimiter=',')
            headers = next(myreader)

    # not strictly necessary, but if you want to verify the file
    return headers


# incomplete
def csv_to_sql(manifest_row, engine, meta):
    """
    Does the actual loading of the file into SQL. This assumes all necessary tests have been passed (i.e. do_fields_match etc.)

   
    If the table doesnt exist, create it, using meta.json data types
    If the table already exists, it should be appended to.
    Date parsing will assume one consistent format provided by cleaned.csv (format TBD)
    """
    pass


# complete, tests not written
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

    meta = load_meta_data('meta_sample.json')
    database_connection = tools.database.get_database_connection('local_database')

    if not check_csv_manifest_unique_ids('manifest.csv'): raise ValueError('Manifest has duplicate unique_data_id')

    for idx, csv_row in enumerate(read_csv_manifest()):
        sql_row = get_sql_manifest_row(database_connection = database_connection, csv_row = csv_row)

        # only load the file if it is not already in the database
        if not should_file_be_loaded(sql_row=sql_row, csv_row = csv_row):
            pass # specific reason will be logged by should_file_be_loaded
        else:
            table_name = csv_row['table_name']
            download_data_file(csv_row)             #performs the download if necessary, throws error if it can't open the file after downloading

            reader = DataReader()
            able_to_load = True  #TODO it would be good to attach this as a property to the DataReader. If any problem occurs we can abandon
            for index, data_row in enumerate(DataReader()):
                # When we first access the data, check the headers match.
                if index == 0:
                    if not do_fields_match(data_row=data_row, meta=meta, table_name=table_name):
                        logging.info('data fields in {} do not match meta.json')
                        able_to_load = False
                        # abandon this file
                        break

                # Continue the for loop - clean rows and add them to cleaned.csv
                pass
                # TODO normalize the date functions for all date field types
                # TODO apply cleaning functions specific to this data file
                # TODO write the row to a temporary cleaned.csv file


            if ready_to_load == True:
                # TODO write the cleaned.csv to the appropriate SQL table
                # TODO add/update the appropriate row to the SQL manifest table indicating new status
                pass

        # temporary code
        if idx > 10: break
        print(csv_row)


if __name__ == '__main__':

    # Eventual structure:
    # the appropriate database name in secrets.json. Should make this changeable via optional positional sys.argv
    database_choice = 'local_database'

    if 'rebuild' in sys.argv:
        drop_tables(database_choice)

    main(database_choice)

    # ------------------
    # testing code follows
    # ------------------

    database_connection = database.get_database_connection('local_database')
    MANIFEST_FILENAME = os.path.join(os.path.dirname(__file__), 'manifest_sample.csv')

    if 'download_test' in sys.argv:
        manifest = read_csv_manifest(MANIFEST_FILENAME)
        csv_row_1 = next(manifest)
        headers = download_data_file(csv_row_1)
        print(headers)


