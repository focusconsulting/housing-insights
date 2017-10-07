"""
This modules defines the base colleague class for use by any object that will
interact with the ingestion mediator module.
"""


class Colleague(object):
    def __init__(self, debug=False):
        self._ingestion_mediator = None
        self._debug = debug

    def set_ingestion_mediator(self, ingestion_mediator):
        self._ingestion_mediator = ingestion_mediator

    def _get_engine(self):
        return self._ingestion_mediator.get_engine()

    def _get_manifest_row(self):
        return self._ingestion_mediator.get_current_manifest_row()
