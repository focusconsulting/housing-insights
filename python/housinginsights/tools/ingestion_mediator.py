"""
This module is an implementation of a mediator object. It interacts
 with all objects and scripts involved in our ingestion and processing
 protocol and coordinate their activities.

 The following are some core tasks:

    - check for new data regularly per specific schedule or on demand when
    requested by admin
    - download and ingest all new data
    - handle all data ingestion problems via logging and skipping
    - alert amdins via email of the data collection status; any
    missing/skipped data sets, any ingestion problems
"""

# python imports
import os
import sys

# relative package import for when running as a script
PYTHON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           os.pardir, os.pardir))
sys.path.append(PYTHON_PATH)
SCRIPTS_PATH = os.path.abspath(os.path.join(PYTHON_PATH, 'scripts'))

from python.housinginsights.ingestion.DataReader import DataReader
from python.housinginsights.ingestion.LoadData import LoadData
from python.housinginsights.ingestion.Manifest import Manifest
from python.housinginsights.ingestion import functions as ingest_func
from python.housinginsights.tools import dbtools
from python.housinginsights.tools.logger import HILogger

logger = HILogger(name=__file__, logfile="ingestion_mediator.log")  # TODO -
# refactor


class IngestionMediator(object):
    def __init__(self, database_choice=None, meta_path=None):
        """
        Initialize mediator with private instance variables for colleague
        objects and other instance variables needed for ingestion workflow
        """
        # load defaults if no arguments passed
        if database_choice is None:
            self._database_choice = 'docker_database'
        else:
            self._database_choice = database_choice
        if meta_path is None:
            meta_path = os.path.abspath(os.path.join(SCRIPTS_PATH,
                                                     'meta.json'))

        # initialize instance variables related from above passed args
        self._meta = ingest_func.load_meta_data(meta_path)
        self._engine = dbtools.get_database_engine(self._database_choice)

        # initialize instance variables for colleague objects
        self._load_data = None
        self._manifest = None

    ###############################
    # set methods for linking this instance with respective colleague instances
    ###############################
    def set_load_data(self, load_data_instance):
        self._load_data = load_data_instance

    def set_manifest(self, manifest_instance):
        self._manifest = manifest_instance

    ###############################
    # methods for coordinating tasks across other objects
    ###############################
    def load_psv_to_database(self, unique_data_id):
        """
        Reloads the flat file associated to the unique_data_id.

        Returns a list of unique_data_ids that were successfully updated.
        """
        logger.info("update_only(): attempting to update {} data".format(
            unique_data_id))

        manifest_row = self._manifest.get_manifest_row(unique_data_id)

        # process manifest row for requested data_id if flagged for use
        if manifest_row is None:
            logger.info("  Skipping: {} not found in manifest!".format(
                unique_data_id))
            return False
        else:
            # follow normal workflow and load data_id
            logger.info(
                "  Loading {} data!".format(unique_data_id))
            self._load_data.process_data_file(manifest_row)

        return True

    def rebuild_database(self, drop_all_tables=False):
        """
        Using manifest.csv and meta.json loads all usable data into the
        database, if requested after dropping all tables.
        """
        if drop_all_tables:
            # TODO - avoid this once refactor is complete
            self._load_data._drop_tables()

        # reload meta.json into db
        self._load_data.meta_json_to_database()

        processed_data_ids = []

        # Iterate through each row in the manifest then clean and validate
        for manifest_row in self._manifest:
            # Note: Incompletely filled out rows in the manifest can break the
            # other code
            # TODO: add validation check in Manifest to flag issue above earlier

            # only clean and validate data files flagged for use in database
            try:
                if manifest_row['include_flag'] == 'use':
                    logger.info(
                        "{}: preparing to load row {} from the manifest".
                        format(manifest_row['unique_data_id'],
                               len(self._manifest)))
                    self._load_data.process_data_file(manifest_row)
                processed_data_ids.append(manifest_row['unique_data_id'])
            except:
                logger.exception("Unable to process {}".format(
                    manifest_row['unique_data_id']))

        return processed_data_ids


if __name__ == '__main__':
    # initialize instances to be used for this ingestion mediator instance
    load_data = LoadData(drop_tables=False)
    manifest = Manifest()

    # initialize an instance of ingestion mediator and set colleague instances
    mediator = IngestionMediator()
    mediator.set_load_data(load_data)
    mediator.set_manifest(manifest)

    # connect colleague instances to this ingestion mediator instance
    load_data.set_ingestion_mediator(mediator)
    manifest.set_ingestion_mediator(mediator)
