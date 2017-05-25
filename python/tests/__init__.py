############################################################
#Folder and file setup/configuration tests
############################################################


import unittest
from unittest import skip

import sys, os

python_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.pardir))
sys.path.append(python_filepath)

class InitializationTests(unittest.TestCase):

    def test_import_ingestion(self):
        """
        Check import 'ingestion' as a whole package
        """
        try:
            from housinginsights import ingestion
        except ImportError:
            self.fail("Was not able to import ingestion")
