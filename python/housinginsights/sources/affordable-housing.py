import csv
import json


from housinginsights.sources.base import BaseApiConn
from housinginsights.sources.models.mar import FIELDS


class AffordableHousingApiConn(object):
    """
    API Interface to the Affordable Housing dataset on opendata.dc.gov.
    """

    BASEURL = 'http://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/' \
              'Property_and_Land_WebMercator/MapServer/62'
    # default query to get all data as json output
    QUERY = '/query?where=1%3D1&outFields=*&outSR=4326&f=json'

    def __init__(self):
        self.conn = BaseApiConn()

    def query_output(self):
        """
        Returns json
        :return:
        """