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

#Configure logging. See /scripts/logs/example-logging.py for examples of how to use this.
logging_filename = "../logs/scripts.log"
logging.basicConfig(filename=logging_filename, level=logging.DEBUG)
logging.warning("--------------------starting module------------------")

