"""
get_api_data.py provides command line convenience access to the modules in the housinginsights.sources
directory.

Every API class should implement a few key features
"""


import sys
import os
import importlib
from datetime import datetime
import argparse


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


def get_multiple_api_sources(a):
    '''
    This method calls the 'get_data' method on each ApiConn class in the /sources folder
    a = an arguments object from argparse

    a.ids: list of unique data ids. Passing 'None' to unique_data_ids will run all get_data methods.
    a.sample: when possible, download just a few lines (for faster testing)
    a.database: the database choice, such as 'docker_database', as identified in the secrets.json.
    a.debug: if True exceptions will be raised. if False, they will be printed but processing will continue.
    a.modules: in addition to the unique_data_ids (which are passed directly to the ApiConn.get_data() method), you can choose to
                 only run listed modules.

    '''
    #Turn the arguments into individual items

    #TODO should update the secrets.json keys to make them simpler so that this mapping is irrelevant
    database_map = {'docker':'docker_database',
                    'docker_local':'docker_with_local_python',
                    'codefordc':'codefordc_remote_admin',
                    'local':'local_database'
                    }

    db = database_map[a.database]
    unique_data_ids=a.ids
    sample = a.sample
    output_type = 'csv' #deprecated, should get rid of stdout option w/in the modules and always use csv
    debug = a.debug
    module_list = a.modules



    logger.info("Starting get_multiple_api_sources.")
    API_FOLDER = 'housinginsights.sources'

    # All possible source modules and classes as key:value of module:classname
    modules = {
            'opendata':       'OpenDataApiConn',
            'DCHousing':      'DCHousingApiConn',
            'dhcd':           'DhcdApiConn',
            'census':         'CensusApiConn',
            'wmata_distcalc': 'WmataApiConn',
            'prescat':        'PrescatApiConn'
    }

    # If no module list is provided, use them all
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
            api_method = getattr(api_instance, 'get_data') # Every class should have a get_data method!

            # Get the data
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
    date_stamped_folder = os.path.join(folder, 'raw', '_downloads', d)
    try:
        manifest.update_manifest(date_stamped_folder=date_stamped_folder)
        logger.info("Manifest updated at %s", date_stamped_folder)
    except Exception as e:
        logger.error("Failed to update manifest with error %s", e)
    logger.info("Completed get_multiple_api_sources.")



#Add a command line argument parser
description = ("""Downloads data from the various sources that are used in Housing Insights. 
                """)
parser = argparse.ArgumentParser(description=description)
parser.add_argument("database", help="""which database we should connect to 
                    when using existing data as part of the download process""",
                    choices=['docker', 'docker_local', 'local', 'codefordc'])

parser.add_argument('-s', '--sample', help="""Only download a sample of data. Used
                                 for testing, but doesn't work for most sources""",
                    action='store_true')

parser.add_argument('--ids', nargs='+',
                    help='Only download these unique data_ids',
                    choices = ['tax',
                              'building_permits_2013','building_permits_2014',
                              'building_permits_2015','building_permits_2016',
                              'building_permits_2017', 'building_permits_2018',
                              'crime_2013','crime_2014','crime_2015',
                              'crime_2016','crime_2017',
                              'mar',
                              'dchousing',
                              'dhcd_dfd_projects', 'dhcd_dfd_properties',
                              'acs5_2009','acs5_2010','acs5_2011','acs5_2012',
                              'acs5_2013','acs5_2014','acs5_2015',
                              'acs5_2009_moe','acs5_2010_moe','acs5_2011_moe','acs5_2012_moe',
                              'acs5_2013_moe','acs5_2014_moe','acs5_2015_moe',
                              'wmata_stops','wmata_dist'
                             ])

parser.add_argument('--modules', nargs='+',
                    help='Only download from these modules',
                    #TODO make choices list pull from the keys of 'modules' var above
                    choices = ['opendata',
                                'DCHousing',
                                'dhcd',
                                'census',
                                'wmata_distcalc',
                                'prescat'
                                ])

parser.add_argument ('--debug',action='store_true',
                    help="Pass this flag to use debug mode, where errors are raised as they occur")



if __name__ == '__main__':
    logger.info("running get api data")

    a = parser.parse_args()
    get_multiple_api_sources(a)
