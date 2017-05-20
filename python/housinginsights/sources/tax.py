import sys, os
from datetime import datetime
from pprint import pprint
import urllib.request

##for testing only
python_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.pardir,os.pardir))

sys.path.append(python_filepath)

from housinginsights.sources.base import BaseApiConn
from housinginsights.sources.models.tax import TaxResult, FIELDS


'''
TODO:

This is currently returning an exceededTransferLimit property, which limits the results to 1,000 records.

Bulk csv download is available from this endpoint, which should be substituted:
https://opendata.arcgis.com/datasets/014f4b4f94ea461498bfeba877d92319_56.geojson
https://opendata.arcgis.com/datasets/014f4b4f94ea461498bfeba877d92319_56.csv

'''

class TaxApiConn(BaseApiConn):
    """
    API Interface to the tax assessment data on opendata.dc.gov.

    Inherits from BaseApiConn class.
    """

    #BASEURL = 'http://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/' \
     #         'Property_and_Land_WebMercator/MapServer/56'
    BASEURL = 'https://opendata.arcgis.com/datasets/014f4b4f94ea461498bfeba877d92319_56.csv'

    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.pardir,os.pardir,os.pardir))


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


    def get_CSV(self, output_type=None, output_file=None):
        """
        Saves CSV of the entire data set.

        :param output_type: Output type specified by user.
        :type  output_type: String.

        :param output_file: Output file specified by user.
        :type  output_file: String
        """

        cur_date = datetime.now().strftime('%Y%m%d')

        output_file = self.output_path+"\\data\\raw\\tax_assessment\\opendata\\{0}".format(cur_date)

        if output_type == 'csv':
            self.add_file(output_file, '\\tax.csv')
            urllib.request.urlretrieve(self.BASEURL, output_file)

        #return dataret