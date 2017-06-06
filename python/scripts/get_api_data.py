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


#TODO is this import necessary?
from housinginsights.config.base import HousingInsightsConfig


def get_multiple_api_sources(unique_data_ids = None,sample=False, output_type = 'csv', db=None, debug=False, module_list = None):
    '''
    This method takes a list of unique_data_ids and calls the 'get_data' method on each ApiConn class in the /sources folder
    By passing a list with one id, you can download (or test) just one API at a time. 
    Passing 'None' to unique_data_ids will run all get_data methods. 

    sample: when possible, download just a few lines (for faster testing)
    output_type: either 'csv' or 'stdout'
    db: the database choice, such as 'docker_database', as identified in the secrets.json. 
    debug: if True exceptions will be raised. if False, they will be printed but processing will continue. 
    module_list: in addition to the unique_data_ids (which are passed directly to the ApiConn.get_data() method), you can choose to 
                 only run listed modules. 

    '''

    API_FOLDER = 'housinginsights.sources'
    
    #All possible source modules and classes as key:value of module:classname
    modules = {
            "wmata_distcalc":"WmataApiConn",
            "opendata":"OpenDataApiConn",
            "DCHousing":"DCHousingApiConn",
            "census":"CensusApiConn"
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
            api_method(unique_data_ids, sample, output_type, db=db)

        except Exception as e:
            logging.warning('The request for "{0}" failed. Error: {1}'.format(m,e))

            if debug==True:
                raise e

if __name__ == '__main__':

    #Set up the appropriate settings for what you want to download

    debug = True            # Errors are raised when they occur instead of only logged.
    unique_data_ids = None   # Alternatively, pass a list of only the data sources you want to download
                            # Available ids:
                            # [ 'dchousing',"tax", "wmata_stops","wmata_dist"
                            #  "building_permits_2013","building_permits_2014","building_permits_2015","building_permits_2016","building_permits_2017"
                            #  "crime_2013","crime_2014","crime_2015","crime_2016","crime_2017", 
                            #  "mar"
                            #  ]

    sample = False          # Some ApiConn classes can just grab a sample of the data for use during development / testing
    output_type = 'csv'     # Other option is stdout which just prints to console
    db = 'docker_database'  # Only used by connections that need to read from the database to get their job done (example: wmata)
    module_list = ["opendata","DCHousing", "census"] #"wmata_distcalc"

    get_multiple_api_sources(unique_data_ids,sample,output_type,db,debug, module_list)

