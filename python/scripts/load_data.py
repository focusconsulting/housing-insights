'''
Utility function for running the LoadData class
'''

#################################
# Configuration
#################################
import sys
import os
import logging
import argparse

PYTHON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           os.pardir))
sys.path.append(PYTHON_PATH)

from housinginsights.ingestion.LoadData import LoadData, main

# configuration: see /logs/example-logging.py for usage examples
logging_path = os.path.abspath(os.path.join(PYTHON_PATH, "logs"))
logging_filename = os.path.abspath(os.path.join(logging_path, "ingestion.log"))
logging.basicConfig(filename=logging_filename, level=logging.INFO)

# Pushes everything from the logger to the command line output as well.
logging.getLogger().addHandler(logging.StreamHandler())


##########################
# Main routine
##########################

description = ('Loads our flat file data into the database of choice. You '
              'can load sample or real data and/or rebuild or update only '
              'specific flat files based on unique_data_id values.')
parser = argparse.ArgumentParser(description=description)
parser.add_argument("database", help='which database the data should be '
                                     'loaded to',
                    choices=['docker', 'docker_local', 'local', 'remote'])
parser.add_argument('-s', '--sample', help='load with sample data',
                    action='store_true')
parser.add_argument('--update-only', nargs='+',
                    help='only update tables with these unique_data_id '
                         'values')
parser.add_argument('--manual', help='Ignore all other arguments and use'
                    'what is hard coded here, for debugging/testing purposes',
                    action='store_true')

arguments = parser.parse_args()


#Normally you won't use this section - this is only for debugging/testing
if arguments.manual:
    print("Using manual settings")
    #Initialization
    scripts_path = os.path.abspath(os.path.join(PYTHON_PATH, 'scripts'))
    meta_path = os.path.abspath(os.path.join(scripts_path, 'meta.json'))
    manifest_path = os.path.abspath(os.path.join(scripts_path, 'manifest.csv'))
    database_choice = 'docker_with_local_python'
    keep_temp_files = True
    drop_tables = True
    loader = LoadData(database_choice=database_choice, meta_path=meta_path,
                      manifest_path=manifest_path, keep_temp_files=keep_temp_files,
                      drop_tables=drop_tables)

    #Do stuff
    api_folder_path = os.path.abspath(os.path.join(PYTHON_PATH, os.pardir, 'data/raw/apis'))
    print(api_folder_path)

    loader.make_manifest(api_folder_path)

#typically we use the approach that is coded into LoadData.py
else:
    # Let the main method handle it
    main(arguments)