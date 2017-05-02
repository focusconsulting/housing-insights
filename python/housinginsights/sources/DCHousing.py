import csv
from pprint import pprint
from datetime import datetime
import os


from python.housinginsights.sources.base import BaseApiConn
from python.housinginsights.sources.models.DCHousing import FIELDS,\
    DCHousingResult


class DCHousingApiConn(object):
    """
    API Interface to the Affordable Housing data set on opendata.dc.gov.
    Use public method to retrieve data.
    """

    BASEURL = 'http://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/' \
              'Property_and_Land_WebMercator/MapServer/62'
    # default query to get all data as json output
    QUERY = '/query?where=1%3D1&outFields=*&outSR=4326&f=json'

    def __init__(self):
        self.conn = BaseApiConn(DCHousingApiConn.BASEURL)

    def get_json(self, output_type=None, output_file=None):
        """
        Returns JSON object of the entire data set
        """
        print("DCHousingApiConn.get_json()")
        result = self.conn.get(DCHousingApiConn.QUERY)
        if result.status_code != 200:
            err = "An error occurred during request: status {0}"
            raise Exception(err.format(result.status_code))

        if output_type == 'stdout':
            print("DCHousingApiConn.get_json() - outtype = stdout")
            pprint(result.json())
        elif output_type == 'csv':
            print("DCHousingApiConn.get_json() - outtype = csv")
            data = result.json()['features']
            results = [DCHousingResult(address['attributes']) for address in
                       data]
            self._result_to_csv(results, output_file)

        return result.json()  # is this necessary - mimicking mar.py

    def _result_to_csv(self, results, csvfile):
        """
        Write the data to a csv file.
        """
        print("DCHousingApiConn._result_to_csv()")
        with open(csvfile, 'w', encoding='utf-8') as f:
            print("DCHousingApiConn._result_to_csv() - write to csv")
            writer = csv.writer(f, delimiter=',')
            writer.writerow(FIELDS)
            for result in results:
                writer.writerow(result.data)
