"""
get_api_data.py provides command line convenience access to the modules in the housinginsights.sources
directory.

Every API class should implement a few key features
"""

# built-in imports
import os
import importlib

# app imports
from housinginsights.tools.base_colleague import Colleague

# Configure logging
from housinginsights.tools.logger import HILogger
logger = HILogger(name=__file__, logfile="sources.log")

PYTHON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           os.pardir))


class GetApiData(Colleague):
    def __init__(self):
        super().__init__()
        self._API_FOLDER = 'housinginsights.sources'
        self._MODULES = {
            'opendata':       'OpenDataApiConn',
            'DCHousing':      'DCHousingApiConn',
            'dhcd':           'DhcdApiConn',
            'census':         'CensusApiConn',
            'wmata_distcalc': 'WmataApiConn',
            'prescat':        'PrescatApiConn'
        }
        self._IDS_TO_MODULES = {
            'tax': 'opendata',
            'building_permits_2013': 'opendata',
            'building_permits_2014': 'opendata',
            'building_permits_2015': 'opendata',
            'building_permits_2016': 'opendata',
            'building_permits_2017': 'opendata',
            'crime_2013': 'opendata',
            'crime_2014': 'opendata',
            'crime_2015': 'opendata',
            'crime_2016': 'opendata',
            'crime_2017': 'opendata',
            'mar': 'opendata',
            'dchousing': 'DCHousing',
            'dhcd_dfd_projects': 'dhcd',
            'dhcd_dfd_properties': 'dhcd',
            'acs5_2009': 'census',
            'acs5_2010': 'census',
            'acs5_2011': 'census',
            'acs5_2012': 'census',
            'acs5_2013': 'census',
            'acs5_2014': 'census',
            'acs5_2015': 'census',
            'acs5_2009_moe': 'census',
            'acs5_2010_moe': 'census',
            'acs5_2011_moe': 'census',
            'acs5_2012_moe': 'census',
            'acs5_2013_moe': 'census',
            'acs5_2014_moe': 'census',
            'acs5_2015_moe': 'census',
            'wmata_stops': 'wmata_distcalc',
            'wmata_dist': 'wmata_distcalc'
        }

    def get_files_by_data_ids(self, unique_data_ids_list):
        processed_ids = list()
        for data_id in unique_data_ids_list:
            try:
                mod = self._IDS_TO_MODULES[data_id]
            except KeyError:
                logger.error('%s is not a valid data id! Skipping...' % data_id)
                continue

            result = self.get_files_by_modules([mod], unique_data_id=[data_id])
            if len(result) == 1:
                processed_ids.append(data_id)
        return processed_ids

    def get_files_by_modules(self, modules_list, unique_data_id=None):
        processed = list()
        for m in modules_list:
            try:
                class_name = self._MODULES[m]
            except KeyError:
                logger.error('Module %s is not valid! Skipping...' % m)
                continue

            try:
                if unique_data_id is None:
                    logger.info("Processing %s module with class %s", m,
                                class_name)
                else:
                    logger.info("Processing %s with class %s", unique_data_id,
                                class_name)
                module_name = self._API_FOLDER + '.' + m
                api_method = self._get_api_method(class_name, module_name)

                # Get the data
                # TODO refactor all the methods that need db to instead use
                # TODO self.engine() created in __init__(see base_project for
                # TODO example)
                api_method(unique_data_id, False, 'csv',
                           db=self._database_choice)
                processed.append(m)

                # log outcome
                if unique_data_id is None:
                    logger.info("Completed processing %s module with class "
                                "%s", m, class_name)
                else:
                    logger.info("Completed processing %s with class "
                                "%s", unique_data_id, class_name)
            except Exception as e:
                logger.error("The request for '%s' failed with error: %s", m, e)

                if self._debug:
                    raise e

        self._ingestion_mediator.update_manifest_with_new_path()
        return processed

    def get_all_files(self):
        modules_list = self._MODULES.keys()
        return self.get_files_by_modules(modules_list)

    def _get_api_method(self, class_name, module_name):
        mod = importlib.import_module(module_name)

        api_class = getattr(mod, class_name)

        api_instance = api_class(database_choice=self._database_choice,
                                 debug=self._debug)
        # IMPORTANT: Every class should have a get_data method!
        return getattr(api_instance, 'get_data')
