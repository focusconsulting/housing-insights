"""
get_api_data.py provides command line convenience access to the modules in the housinginsights.sources
directory.

Every API class should implement a few key features
"""


import sys
import os
import importlib
import logging

python_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.pardir))
sys.path.append(python_filepath)

# Configure logging
logging_path = os.path.abspath(os.path.join(python_filepath, "logs"))
logging_filename = os.path.abspath(os.path.join(logging_path, "sources.log"))
logging.basicConfig(filename=logging_filename, level=logging.DEBUG)
# Pushes everything from the logger to the command line output as well.
logging.getLogger().addHandler(logging.StreamHandler())


#TODO is this necessary?
from housinginsights.config.base import HousingInsightsConfig


def get_multiple_api_sources(unique_data_ids = None,sample=False, output_type = 'csv', debug=False, module_list = None):
    API_FOLDER = 'housinginsights.sources'
    
    #All possible source modules and classes as key:value of module:classname
    modules = {
            "opendata":"OpenDataApiConn",
            "DCHousing":"DCHousingApiConn"
    }

    #If no module list is provided, use them all
    if module_list == None:
        module_list = list(modules.keys())

    for m in module_list:
        try:
            module_name = API_FOLDER + '.' + m
            module = importlib.import_module(module_name)

            class_name = modules[m]
            api_class = getattr(module, class_name)

            api_instance = api_class()
            api_method = getattr(api_instance, 'get_data') #Every class should have a get_data method! 

            #Get the data
            api_method(unique_data_ids, sample, output_type)

        except Exception as e:
            logging.warning('The request for "{0}" failed. Error: {1}'.format(m,e))

            if debug==True:
                raise e

if __name__ == '__main__':
    debug = True            #Errors are raised when they occur instead of only logged.
    unique_data_ids = None  #Alternatively, pass a list of only the data sources you want to download
    sample = False          #Some ApiConn classes can just grab a sample of the data for use during development / testing
    output_type = 'csv'     #Other option is stdout which just prints to console


    get_multiple_api_sources(unique_data_ids,sample,output_type,debug)

