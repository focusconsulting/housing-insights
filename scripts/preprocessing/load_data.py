##########################################################################
## Summary
##########################################################################

'''
Python scripts are used to pre-process existing data sources into formats that we need to call from the on-page javascript. 
'''


##########################################################################
## Imports & Configuration
##########################################################################
import logging
import json
import pandas as pd
from sqlalchemy import create_engine

#Configure logging. See /logs/example-logging.py for examples of how to use this.
logging_filename = "../logs/ingestion.log"
logging.basicConfig(filename=logging_filename, level=logging.DEBUG)
logging.warning("--------------------starting module------------------")
#Pushes everything from the logger to the command line output as well.
logging.getLogger().addHandler(logging.StreamHandler())

#############################
#CONSTANTS
#############################
constants = {
    'snapshots_csv_filename': 'snapshots_to_load_test.csv',
}

def get_connect_str(path='./secrets.json'):
    "Loads the secrets json file to retrieve the connection string"
    logging.info("Loading secrets from {}".format(path))
    with open(path) as fh:
        secrets = json.load(fh)
    return secrets['database']['connect_str']


def csv_to_sql(index_path):
    # Get the list of files to load - using Pandas dataframe (df), although we don't need most of the functionality that Pandas provides. #Example of how to access the filenames we will need to use: print(paths_df.get_value(0,'contracts_csv_filename'))
    paths_df = pd.read_csv(index_path, parse_dates=['date'])
    logging.info("Preparing to load " + str(len(paths_df.index)) + " files")

    # Connect to SQL - uses sqlalchemy so that we can write from pandas dataframe.
    connect_str = get_connect_str()
    engine = create_engine(connect_str)

    for index, row in paths_df.iterrows():
        full_path = row['path'] + row['filename']
        tablename = row['table_name']
        logging.info("loading table " + str(index + 1) + " (" + tablename + ")")
        contracts_df = pd.read_csv(full_path) # parse_dates=['tracs_effective_date','tracs_overall_expiration_date','tracs_current_expiration_date']
        logging.info("  in memory...")
        contracts_df.to_sql(tablename, engine, if_exists='replace')
        logging.info("  table loaded")


if __name__ == '__main__':
    #sample_add_to_database()
    csv_to_sql(constants['snapshots_csv_filename'])
