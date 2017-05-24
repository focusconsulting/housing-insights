from pprint import pprint
import os
import sys
import requests
import datetime

PYTHON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
sys.path.append(PYTHON_PATH)

from housinginsights.sources.base import BaseApiConn
from housinginsights.sources.models.mar import MarResult, FIELDS


class MarApiConn(BaseApiConn):
    """
    API Interface to the Master Address Record (MAR) database.
    Use public methods to retrieve data.
    """

    BASEURL = 'http://citizenatlas.dc.gov/newwebservices/locationverifier.asmx'

    def __init__(self):
        super().__init__(MarApiConn.BASEURL)

    def get_data(self, square, lot, suffix):
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
        # if output_type == 'stdout':
        #     pprint(result.json())
        # elif output_type == 'csv':
        #     data = result.json()['returnDataset']['Table1']
        #     results = [MarResult(address) for address in data]
        #     self.result_to_csv(FIELDS, results, output_file)
        mar_data = result.json()
        if mar_data['returnDataset'] == {}:
            mar_returns = {'Warning': 'No MAR data availble - property under construction - see AYB year'}
        else:
            entry = mar_data['returnDataset']['Table1'][0]
            mar_returns = {'ANC': entry['ANC'],
                           'CENSUS_TRACT': entry['CENSUS_TRACT'],
                           'CLUSTER_': entry['CLUSTER_'],
                           'WARD': entry['WARD'],
                           'ZIPCODE': entry['ZIPCODE']
            }

        return mar_returns

class CamaApiConn(BaseApiConn):
    """
    API Interface to the Master Address Record (MAR) database.
    Use public methods to retrieve data.
    """

    BASEURL = 'https://opendata.arcgis.com/datasets/c5fb3fbe4c694a59a6eef7bf5f8bc49a_25.geojson'

    def __init__(self):
        super().__init__(CamaApiConn.BASEURL)

    def get_data(self):

        mar_api = MarApiConn()

        result = self.get(urlpath=None, params=None)
        if result.status_code != 200:
            err = "An error occurred during request: status {0}"
            raise Exception(err.format(result.status_code))
        cama_data = result.json()

        dict_res = {}  # creates dict of residential data with SSL as primary key
        for row in cama_data['features']:
            objectid = row['properties']['OBJECTID']
            square, lot = row['properties']['SSL'].split()
            suffix = ' '
            if len(square) > 4:
                square = square[:4]
                suffix = square[-1]
            mar_return = mar_api.get_data(square, lot, suffix)
            row['properties'].update(mar_return)
            dict_res[row['properties']['OBJECTID']] = row['properties']
            if len(dict_res) == 50:
                zoneCount(dict_res)

def zoneCount(dict):

    zone_types = ['ANC', 'CENSUS_TRACT', 'CLUSTER_', 'WARD', 'ZIPCODE']


    count_dict = {

    }

    for zone in zone_types:
        for property in dict:
            if 'Warning' not in dict[property].keys():
                count_dict.setdefault(dict[property][zone], {})
                count_dict[dict[property][zone]].setdefault(zone + '_count', 0)
                count_dict[dict[property][zone]][zone + '_count'] += 1

                count_dict[dict[property][zone]].setdefault('unit_count', 0)
                if dict[property]['NUM_UNITS'] == 0:
                    dict[property]['NUM_UNITS'] = 1
                count_dict[dict[property][zone]]['unit_count'] += dict[property]['NUM_UNITS']

                count_dict[dict[property][zone]].setdefault('bedroom_count', 0)
                if dict[property]['BEDRM'] == 0:
                    dict[property]['BEDRM'] = 1
                count_dict[dict[property][zone]]['bedroom_count'] += dict[property]['BEDRM']

    print('test')

my_api = CamaApiConn()
cama_return = my_api.get_data()

