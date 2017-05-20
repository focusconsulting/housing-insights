from pprint import pprint
import os
import sys
import requests


PYTHON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
sys.path.append(PYTHON_PATH)

from housinginsights.sources.base import BaseApiConn
from housinginsights.sources.models.mar import MarResult, FIELDS


class CamaApiConn(BaseApiConn):
    """
    API Interface to the Master Address Record (MAR) database.
    Use public methods to retrieve data.
    """

    BASEURL = 'http://citizenatlas.dc.gov/newwebservices/locationverifier.asmx'

    def __init__(self):
        super().__init__(CamaApiConn.BASEURL)

    def get_data(self, square, lot, suffix, output_type=None,
                      output_file=None):
        """
        Get information on a location based on a simple query string.

        :param square: SSL first part
        :type  location: String.

        :param lot: SSL second part
        :type  location: String.

        :param output_type: Output type specified by user.
        :type  output_type: String.

        :param output_file: Output file specified by user.
        :type  output_file: String

        :returns: Json output from the api.
        :rtype: String
        """
        params = {
            'f': 'json',
            'Square': square,
            'Lot': lot,
            'Suffix': suffix
        }
        result = self.get('/findAddFromSSL2', params=params)
        if result.status_code != 200:
            err = "An error occurred during request: status {0}"
            raise Exception(err.format(result.status_code))
        if output_type == 'stdout':
            pprint(result.json())
        elif output_type == 'csv':
            data = result.json()['returnDataset']['Table1']
            results = [MarResult(address) for address in data]
            self.result_to_csv(FIELDS, results, output_file)
        mar_data = result.json()
        

def cama_data():

    my_api = CamaApiConn()

    residential = 'https://opendata.arcgis.com/datasets/c5fb3fbe4c694a59a6eef7bf5f8bc49a_25.geojson'
    r = requests.get(residential)
    residential_data = r.json()

    dict_res = {}  # creates dict of residential data with SSL as primary key
    for row in residential_data['features']:
        dict_res.setdefault(row['properties']['SSL'], {})
        square, lot = row['properties']['SSL'].split()
        suffix = ' '
        if len(square) > 4:
            square = square[:4]
            suffix = square[-1]
        data_return = my_api.get_data(square, lot, suffix)
        #dict_res[row['properties']['SSL']] = row['properties']

cama_data()

#data = my_api.get_data('findAddFromSSL2')
