##########################################################################
## Summary
##########################################################################

'''
Loads our flat file data into the Postgres database
'''


##########################################################################
## Imports & Configuration
##########################################################################
import logging
import json
import pandas as pd
from sqlalchemy import create_engine
import csv
from urllib.request import urlretrieve

#Configure logging. See /logs/example-logging.py for examples of how to use this.
logging_filename = "../logs/ingestion.log"
logging.basicConfig(filename=logging_filename, level=logging.DEBUG)
logging.warning("--------------------starting module------------------")
#Pushes everything from the logger to the command line output as well.
logging.getLogger().addHandler(logging.StreamHandler())

#Allow modules to import each other at parallel file structure (TODO clean up this configuration in a refactor, it's messy...)
from inspect import getsourcefile
import os.path
import sys
current_path = os.path.abspath(getsourcefile(lambda:0))
current_dir = os.path.dirname(current_path)
parent_dir = current_dir[:current_dir.rfind(os.path.sep)]
repo_dir = parent_dir[:parent_dir.rfind(os.path.sep)]
sys.path.insert(0, parent_dir)

import database_management

#############################
#CONSTANTS
#############################
constants = {
    'manifest_filename': 'snapshots_manifest.csv',
    'date_headers_filename': 'postgres_date_headers.json',
}


#############################
#FUNCTIONS
#############################
def get_column_names(path):
    with open(path) as f:
        myreader=csv.reader(f,delimiter=',')
        headers = next(myreader)
    return headers

def manifest_to_sql(manifest_path, database_choice):
    # Get the list of files to load - using Pandas dataframe (df)
    paths_df = pd.read_csv(manifest_path, parse_dates=['date'])
    connect_str = database_management.get_connect_str(database_choice)
    engine = create_engine(connect_str)


def csv_to_sql(manifest_path, database_choice):
    # Get the list of files to load - using Pandas dataframe (df)
    print (manifest_path)
    paths_df = pd.read_csv(manifest_path, parse_dates=['date'])
    manifest_df_copy = paths_df #this copy will be added to the SQL manifest
    logging.info("Preparing to load " + str(len(paths_df.index)) + " files")

    # Connect to SQL - uses sqlalchemy so that we can write from pandas dataframe.
    connect_str = database_management.get_connect_str(database_choice)
    engine = create_engine(connect_str)



    for index, row in paths_df.iterrows():
        logging.info("checking: " + row['data_version'])
        #######################
        #Decide whether to load the row
        #######################
        load_row = False
        if (row['skip'] == "skip") or (row['skip'] == "invalid"):
            load_row = False
        #See if the table is already loaded by checking the database table
        elif (row['skip'] == "use"):

            database_connection = engine.connect()
            if engine.dialect.has_table(database_connection, 'manifest'):
                query_result = database_connection.execute("select skip from manifest where data_version='{}'".format(row['data_version']))

                for query_row in query_result:
                    database_skip_val = query_row['skip']

                if database_skip_val == "loaded":
                    load_row = False
                    manifest_df_copy.set_value(index, 'skip', 'loaded') #make sure we write 'loaded' to the manifest table when we finish this procedure (instead of 'use')
                else:
                    load_row = True
            else:
                #the 'manifest' table doesn't exist, so we are probably recreating the database for the first time
                load_row = True
            database_connection.close()
        else:
            load_row =True

        #######################
        #Load the file from disk into the database
        #######################
        if load_row == False:
            logging.info("  skipping table")
        else:
            full_path = repo_dir + row['local_folder'] + row['subpath'] + row['filename']
            tablename = row['table_name']
            logging.info("  attempting to load table")

            #Since different files have different date columns, we need to compare to the master list.
            #Since this is the first time we use the file, try downloading it if it fails
            try:
                headers = list(get_column_names(full_path))
            except FileNotFoundError as e:
                s3_path = row['s3_folder'] + row['subpath'] + row['filename']
                logging.info("  file not found. attempting to download file to disk: " + s3_path)
                urlretrieve(s3_path,full_path)
                logging.info("  download complete. Loading table " + str(index + 1) + " (" + tablename + ": "+ row['data_version'] + ")")
                headers = list(get_column_names(full_path))

            with open(current_dir + "\" + constants['date_headers_filename']) as fh:
                date_headers = json.load(fh)
                parseable_headers = date_headers['date_headers']
            to_parse = list(set(parseable_headers) & set(headers))
            logging.info("  parsing date columns: " + str(to_parse))

            ###
            #Load the data into memory
            ###
            #This is the same as the default parser, but missing values are null instead of throwing an error.
                #infer_datetime_format is used to speed up loading if you expect all dates to be in the same format
            parser = lambda x: pd.to_datetime(x, errors='coerce', infer_datetime_format=True)

            #load the file
            csv_df = pd.read_csv(full_path, encoding="latin1", parse_dates=to_parse, date_parser=parser)
            logging.info("  in memory...")

            #convert column names to follow SQL best practices
            csv_df.columns = map(str.lower, csv_df.columns)
            csv_df.columns = [c.replace(' ', '_') for c in csv_df.columns]
            csv_df.columns = [c.replace('.', '_') for c in csv_df.columns]

            #Force fields with $ from text to numeric
            currency_fields = ['0br_fmr','1br_fmr','2br_fmr','3br_fmr','4br_fmr']
            if set(currency_fields).issubset(csv_df.columns):
                logging.info("  found currency fields: " + str(currency_fields))
                for fieldname in currency_fields:
                    csv_df[fieldname].replace(to_replace='[\$,)]',value='', inplace=True, regex=True )
                    csv_df[fieldname] = pd.to_numeric(csv_df[fieldname])
            logging.info("  table cleanup complete...")


            #add a column so that we can put all the snapshots in the same table
            csv_df['data_version'] = row['data_version']
            csv_df.to_sql(tablename, engine, if_exists='append')
            logging.info("  table loaded into database")

            manifest_df_copy.set_value(index, 'skip', 'loaded')

    #Done looping rows. Add manifest to database
    manifest_df_copy.to_sql('manifest', engine, if_exists='replace')


if __name__ == '__main__':
    csv_to_sql(current_dir + "\" + constants['manifest_filename'], 'database')
