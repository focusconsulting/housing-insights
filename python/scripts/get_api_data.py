"""
get_api_data.py provides command line convenience access to the modules in the housinginsights.sources
directory.

Every API class should implement a few key features
"""


import sys
import os
import importlib
from datetime import datetime


python_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.pardir))
sys.path.append(python_filepath)

# Configure logging
import logging
from housinginsights.tools.logger import HILogger
logger = HILogger(name=__file__, logfile="sources.log", level=logging.INFO)

#TODO is this import necessary?
from housinginsights.config.base import HousingInsightsConfig
from housinginsights.ingestion.Manifest import Manifest
from housinginsights.tools.mailer import HIMailer

def get_multiple_api_sources(unique_data_ids=None, sample=False, output_type='csv', db=None, debug=False, module_list=None):
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
    logger.info("Starting get_multiple_api_sources.")
    API_FOLDER = 'housinginsights.sources'

    # All possible source modules and classes as key:value of module:classname
    modules = {
            'opendata':       'OpenDataApiConn',
            'DCHousing':      'DCHousingApiConn',
            'dhcd':           'DhcdApiConn',
            'census':         'CensusApiConn',
            'wmata_distcalc': 'WmataApiConn'
    }

    #If no module list is provided, use them all
    if module_list is None:
        module_list = list(modules.keys())

    for m in module_list:
        try:
            logger.info("Processing %s module with class %s", m, modules[m])
            module_name = API_FOLDER + '.' + m
            module = importlib.import_module(module_name)

            class_name = modules[m]
            api_class = getattr(module, class_name)

            api_instance = api_class(database_choice=db, debug=debug)
            api_method = getattr(api_instance, 'get_data') #Every class should have a get_data method!

            #Get the data
            api_method(unique_data_ids, sample, output_type, db=db) #TODO refactor all the methods that need db to instead use self.engine() created in __init__(see base_project for example)

        except Exception as e:
            logger.error("The request for '%s' failed with error: %s", m, e)

            if debug:
                raise e

    # update the manifest
    manifest = Manifest(os.path.abspath(os.path.join(
        python_filepath, 'scripts', 'manifest.csv')))
    d = datetime.now().strftime('%Y%m%d')

    # use correct root folder for raw folder path
    if db == 'remote_database':
        folder = 'https://s3.amazonaws.com/housinginsights'
    else:
        folder = os.path.join(python_filepath, os.pardir, 'data')
    date_stamped_folder = os.path.join(folder, 'raw', 'apis', d)
    try:
        manifest.update_manifest(date_stamped_folder=date_stamped_folder)
        logger.info("Manifest updated at %s", date_stamped_folder)
    except Exception as e:
        logger.error("Failed to update manifest with error %s", e)
    logger.info("Completed get_multiple_api_sources.")

def send_log_file_to_admin(debug=True):
    "At conclusion of process, send log file by email to admin and delete or archive from server."
    if os.path.exists(logger.logfile):
        level_counts = get_log_level_counts(logger.logfile)
        error_count = level_counts.get('ERROR', 0)
        email = HIMailer(debug_mode=debug)
        #email.recipients.append('neal@nhumphrey.com')
        email.subject = "get_api_data logs, completed with {} errors".format(error_count)
        email.message = "See attached for the logs from get_api_data.py. Log counts by level are as follows: {}".format(level_counts)
        email.attachments = [logger.logfile]
        email.send_email()
        #This line is throwing a file busy error. TODO we should archive these log files instead of deleting. 
        #os.unlink(logger.logfile)

def get_log_level_counts(logfile):
    with open(logfile) as log:
        logdata = log.readlines()
        level_counts = {}
        for record in logdata:
            level = record.split(' ')[0]
            if level_counts.get(level):
                level_counts[level] += 1
            else:
                level_counts[level] = 1
    return level_counts

if __name__ == '__main__':
    # test_send()
    logger.info("running get api data")

    # Set up the appropriate settings for what you want to download
    debug = False            # Raise errors instead of only logging them
    unique_data_ids = None #['dchousing'] #None  # Alternatively, pass a list of only the
                            # data sources you want to download:
                            # Supported ids:
                            # ['tax',
                            #  'building_permits_2013','building_permits_2014',
                            #  'building_permits_2015','building_permits_2016',
                            #  'building_permits_2017',
                            #  'crime_2013','crime_2014','crime_2015',
                            #  'crime_2016','crime_2017',
                            #  'mar',
                            #  'dchousing',
                            #  'dhcd_dfd_projects', 'dhcd_dfd_properties',
                            #  'acs5_2009','acs5_2010','acs5_2011','acs5_2012',
                            #  'acs5_2013','acs5_2014','acs5_2015',
                            #  'acs5_2009_moe','acs5_2010_moe','acs5_2011_moe','acs5_2012_moe',
                            #  'acs5_2013_moe','acs5_2014_moe','acs5_2015_moe',
                            #  'wmata_stops','wmata_dist',
                            #  'mar'
                            # ]
    sample = False          # Some ApiConn classes can just grab a sample of the data for dev/testing
    output_type = 'csv'     # Other option is 'stdout' which just prints to console
    db = 'docker_database'  # Only used by connections that need to read from the database to get their job done (example: wmata)
    module_list = ['dhcd'] # ['opendata','DCHousing','dhcd','census'] #['wmata_distcalc']
    try:
        get_multiple_api_sources(unique_data_ids,sample,output_type,db,debug, module_list)
        send_log_file_to_admin(debug=debug)
    except Exception as e:
        logger.error("get_api_data failed with error: %s", e)
        send_log_file_to_admin(debug=debug)
        if debug:
            raise e


