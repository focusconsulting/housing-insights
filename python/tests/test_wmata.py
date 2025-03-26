import unittest
import os
import sys
from io import StringIO
import subprocess
import logging

# setup some useful absolute paths

PYTHON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
# add to python system path
sys.path.append(PYTHON_PATH)

from housinginsights.sources.wmata_distcalc import WmataApiConn


class TestWmataCase(unittest.TestCase):

    def setUp(self):
        self.wmata_api = WmataApiConn()
        self.dist_file = "./dist_results"
        self.stops_file = "./stops_results"
        # self.data_log_file = 'data_test_wmata.log'

        # self.logger = logging.getLogger()
        # self.logger.level = logging.INFO
        # self.logger_handler = logging.StreamHandler()  # Handler for the logger
        # self.logger.addHandler(self.logger_handler)
        # logging.basicConfig(format='%(message)s',filename=self.wmata_log_file,level=logging.INFO)

    # def test_get_data(self):
    #     self.test_stops()
    #     self.test_dist()

    def tearDown(self):
        pass
        # Remove log files
        # os.remove(self.stops_log_file)
        # os.remove(self.dist_log_file)
        # os.remove(self.data_log_file)

    def test_stops(self):

        # for handler in self.logger.handlers:
        #     handler.flush()

        # Set log config
        # self.logger_handler.setFormatter(logging.Formatter('Stops: %(message)s'))
        # self.logger_handler.set
        # logging.basicConfig(filename=self.stops_log_file)

        # Run stops method

        self.wmata_api.get_stops(["wmata_stops"], True, self.stops_file)

        ### Pull the contents back into a string and close the stream
        # log_contents = log_capture_string.getvalue()
        # log_capture_string.close()

        # Open test log file
        with open(self.stops_file) as log:
            log_content = log.readlines()

        # Check to make sure the column names are correct
        # Check to make sure it started pulling metro stops
        # Check to make sure it started pulling bus stops
        foundHeader = False
        foundMetroCenter = False
        found6790 = False
        busStops = 0
        railStops = 0
        for line in log_content:
            if "stop_id_or_station_code,type,name,latitude,longitude,line" in line:
                foundHeader = True
            elif "A01,rail,Metro Center,38.898303,-77.028099,RD" in line:
                foundMetroCenter = True
            elif "5000375,bus,COMMERCIAL DR + #6790,38.800485,-77.177556,18J" in line:
                found6790 = True

            if "bus" in line:
                busStops += 1
            elif "rail" in line:
                railStops += 1
        self.assertTrue(foundHeader)
        self.assertTrue(foundMetroCenter)
        self.assertTrue(found6790)

        # Check to make sure the number of stops is roughly the same
        # This allows for some variation in stops, in case any are closed or open, but would need to be modified for big changes
        busStopsTrue = False
        railStopsTrue = False
        if busStops > 10590:
            busStopsTrue = True
        if railStops > 90:
            railStopsTrue = True
        self.assertTrue(busStopsTrue)
        self.assertTrue(railStopsTrue)

        os.remove(self.stops_file)

    def test_dist(self):

        # for handler in self.logger.handlers:
        #     handler.flush()

        # #Set log config
        # self.logger_handler.setFormatter(logging.Formatter('Dist: %(message)s'))
        # logging.basicConfig(filename=self.dist_log_file)

        # Run dist method
        self.wmata_api.get_dist(["wmata_dist"], True, self.dist_file, "docker_database")

        # Open test log file
        with open(self.dist_file) as log:
            log_content = log.readlines()

        # Check to make sure the column names are correct
        # Check to make sure it started pulling metro stops
        # Check to make sure it started pulling bus stops
        foundHeader = False
        foundMetroCenter = False
        found6790 = False
        busStops = 0
        railStops = 0
        for line in log_content:
            if "nlihc_id,type,stop_id_or_station_code,dist_in_miles" in line:
                foundHeader = True
            elif "NL000001,rail,E01,0.19" in line:
                foundMetroCenter = True
            elif "NL000001,bus,1001396,0.02" in line:
                found6790 = True

            if ",bus," in line:
                busStops += 1
            elif ",rail," in line:
                railStops += 1
        self.assertTrue(foundHeader)
        self.assertTrue(foundMetroCenter)
        self.assertTrue(found6790)

        # Check to make sure the number of stops is roughly the same
        # This allows for some variation in stops, in case any are closed or open, but would need to be modified for big changes
        busStopsTrue = False
        railStopsTrue = False
        if busStops > 50:
            busStopsTrue = True
        if railStops >= 2:
            railStopsTrue = True
        self.assertEqual(busStops, 51)
        self.assertEqual(railStops, 2)

        os.remove(self.dist_file)


if __name__ == "__main__":
    unittest.main()
