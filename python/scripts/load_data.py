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

from housinginsights.ingestion.LoadData import LoadData, main, parser

# configuration: see /logs/example-logging.py for usage examples
logging_path = os.path.abspath(os.path.join(PYTHON_PATH, "logs"))
logging_filename = os.path.abspath(os.path.join(logging_path, "ingestion.log"))
logging.basicConfig(filename=logging_filename, level=logging.INFO)

# Pushes everything from the logger to the command line output as well.
logging.getLogger().addHandler(logging.StreamHandler())

#For command line arguments available, see the 'parser' at end of LoadData.py

if __name__ == '__main__':
  arguments = parser.parse_args()
  main(arguments)

