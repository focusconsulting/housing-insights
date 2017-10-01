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

from python.housinginsights.ingestion.LoadData import LoadData
from python.housinginsights.ingestion.Manifest import Manifest


class IngestionMediator(object):
    def __init__(self):
        """
        Initialize mediator with private instance variables for colleague
        objects
        """
        self._load_data = None
        self._manifest = None
        self._data_base_choice = 'docker_database'

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
    pass


if __name__ == '__main__':
    # initialize instances to be used for this ingestion mediator instance
    load_data = LoadData()
    manifest = Manifest()

    # initialize an instance of ingestion mediator and set colleague instances
    mediator = IngestionMediator()
    mediator.set_load_data(load_data)
    mediator.set_manifest(manifest)

    # connect colleague instances to this ingestion mediator instance
    load_data.set_ingestion_mediator(mediator)
    manifest.set_ingestion_mediator(mediator)
