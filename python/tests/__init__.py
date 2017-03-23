############################################################
#Folder and file setup/configuration tests
############################################################


import unittest
from unittest import skip

import sys, os
sys.path.append(os.path.abspath('./'))

class InitializationTests(unittest.TestCase):

    def test_import_ingestion(self):
        """
        Check import 'ingestion' as a whole package
        """
        try:
            from housinginsights import ingestion
        except ImportError:
            self.fail("Was not able to import ingestion")
