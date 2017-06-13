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
logging.basicConfig(filename=logging_filename, level=logging.DEBUG)

# Pushes everything from the logger to the command line output as well.
logging.getLogger().addHandler(logging.StreamHandler())


##########################
# Main routine
##########################

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
