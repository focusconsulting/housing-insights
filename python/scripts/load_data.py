"""
Utility function for running the LoadData class
"""

#################################
# Configuration
#################################
import sys
import os
import argparse

PYTHON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(PYTHON_PATH)

from housinginsights.ingestion.LoadData import LoadData, main, parser

# For command line arguments available, see the 'parser' at end of LoadData.py

if __name__ == "__main__":
    arguments = parser.parse_args()
    main(arguments)
