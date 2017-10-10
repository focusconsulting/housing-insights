"""
This modules defines the base colleague class for use by any object that will
interact with the ingestion mediator module.
"""


class Colleague(object):
    def __init__(self, debug=False):
        self._ingestion_mediator = None
        self._debug = debug
        self._engine = None
        self._database_choice = None

    def set_ingestion_mediator(self, ingestion_mediator):
        self._ingestion_mediator = ingestion_mediator
        self._engine = self._get_engine()
        self._database_choice = self._ingestion_mediator.get_database_choice()
        self._debug = self._ingestion_mediator.get_debug()

    def _get_engine(self):
        return self._ingestion_mediator.get_engine()

    def _get_manifest_row(self):
        return self._ingestion_mediator.get_current_manifest_row()
