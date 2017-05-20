import csv
from datetime import datetime
from pprint import pprint

from housinginsights.sources.base import BaseApiConn
from housinginsights.sources.models.tax import TaxResult, FIELDS





'''
TODO:

This is currently returning an exceededTransferLimit property, which limits the results to 1,000 records. 

Bulk csv download is available from this endpoint, which should be substituted:
https://opendata.arcgis.com/datasets/014f4b4f94ea461498bfeba877d92319_56.geojson

'''

class TaxApiConn(BaseApiConn):
    """
    API Interface to the tax assessment data on opendata.dc.gov.

    Inherits from BaseApiConn class.
    """

    BASEURL = 'http://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/' \
              'Property_and_Land_WebMercator/MapServer/56'

    def __init__(self):
        super().__init__(TaxApiConn.BASEURL)

    def get_tad(self, output_type=None, output_file=None):
        """
        Returns JSON object of the entire data set.

        :param output_type: Output type specified by user.
        :type  output_type: String.

        :param output_file: Output file specified by user.
        :type  output_file: String

        :returns: Json output from the api.
        :rtype: String
        """
        cur_date = datetime.now().strftime('%Y%m%d')
        params = {
            'f': 'json',
            'where': '1=1',
            'outFields': '*',
            'outSR': '4326'
        }
        result = self.get('/query', params=params)
        print(result)
        if result.status_code != 200:
            err = "An error occurred during request: status {0}"
            raise Exception(err.format(result.status_code))
        if output_type == 'stdout':
            pprint(result.json())
        elif output_type == 'csv':
            data = result.json()['features']
            results = [TaxResult(section['attributes']) for section in data]
            output_file = "../../data/raw/tax_assessment/opendata/{0}.csv".format(cur_date)
            self.result_to_csv(FIELDS, results, output_file)

        return result.json()
