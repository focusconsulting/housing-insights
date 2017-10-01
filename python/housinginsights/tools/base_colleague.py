"""
This modules defines the base colleague class for use by any object that will
interact with the ingestion mediator module.
"""


class Colleague(object):
    def __init__(self):
        self._ingestion_mediator = None

    def set_ingestion_mediator(self, ingestion_mediator):
        self._ingestion_mediator = ingestion_mediator
