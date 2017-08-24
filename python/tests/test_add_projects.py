import unittest
import os
import sys

PYTHON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           os.pardir))
# add to python system path
sys.path.append(PYTHON_PATH)

from housinginsights.ingestion.LoadData import LoadData
from housinginsights.ingestion.Cleaners import ProjectCleaner


class TestAddProjects(unittest.TestCase):
    def setUp(self):
        pass

    def test_whatever(self):
        pass
        

if __name__ == '__main__':
    unittest.main()
