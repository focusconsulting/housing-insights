import unittest
import os
import sys

PYTHON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
# add to python system path
sys.path.append(PYTHON_PATH)


class TestApiEndpoints(unittest.TestCase):
    def setUp(self):
        self.testable_endpoints = [
            "/api/meta"
            # filter_blueprint.py
            ,
            "/api/filter"
            # zone_facts_blueprint.py
            ,
            "/api/census/poverty_rate/ward",
            "/api/census/poverty_rate/neighborhood_cluster",
            "/api/census/poverty_rate/census_tract"
            # project_view_blueprint.py
            ,
            "/api/wmata/NL000092",
            "/api/building_permits/0.5?latitude=38.923&longitude=-76.997",
            "/api/projects/0.5?latitude=38.923&longitude=-76.997",
            "/api/count/crime/all/12/ward",
            "/api/count/building_permits/construction/12/neighborhood_cluster",
        ]

    def test_endpoints(self):
        pass
        # TODO write test so that it makes sure there is no failure from endpoint, at least returns something


if __name__ == "__main__":
    unittest.main()
