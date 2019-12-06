'''
Lamdba for creating and updating the housing insights data sources
'''

#################################
# Configuration
#################################
import sys
import os
import argparse

PYTHON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           os.pardir))
sys.path.append(PYTHON_PATH)

from housinginsights.ingestion.LoadData import LoadData, main, parser

def lambdaHandler(event, context):
  arguments = parser.parse_args()
  main(arguments)