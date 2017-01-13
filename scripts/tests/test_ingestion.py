##########################################################################
## Ingestion Package Tests
##########################################################################

# to execute tests, cd to the /scripts folder. This runs all test packages
# (this one and any other in the /tests folder)
#
#   nosetests --verbosity=2 --with-coverage --cover-inclusive --cover-erase tests
#
# for a list of available asserts:
# https://docs.python.org/2/library/unittest.html#assert-methods




##########################################################################
## Imports
##########################################################################

import unittest
from unittest import skip

#Example import from our data structure
import ingestion.load_data
#from ingestion.load_data import MyObjectName

##########################################################################
## Tests
##########################################################################

class IngestionTests(unittest.TestCase):


    def test_can_run_tests(self):
        """
        Make sure that tests works for test_ingestion.py
        """
        print("I am running")
        assert(True)

    @skip('Test not written yet')
    def test_loads_data(self):
        """
        Just an example of a test we might want to write.
        """
        pass
