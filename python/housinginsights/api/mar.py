
import csv

from housinginsights.api.base import BaseApiConn
from housinginsights.api.models.mar import MarResult, FIELDS


class MarApiConn(object):

    BASEURL = 'http://citizenatlas.dc.gov/newwebservices/locationverifier.asmx'

    def __init__(self):
        self.conn = BaseApiConn(MarApiConn.BASEURL)

    def find_location(self, location, output=None):
        params = {
            'f': 'json',
            'str': location
        }
        result = self.conn.get('/findLocation2', params=params)
        if result.status_code != 200:
            err = "An error occurred during request: status {0}"
            raise Exception(err.format(result.status_code))
        data = result.json()['returnDataset']['Table1']
        results = [MarResult(address) for address in data]
        if output is not None:
            self.result_to_csv(results, output)
        return results

    def result_to_csv(self, result, csvfile):
        with open(csvfile, 'w') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(FIELDS)
            for result in result:
                writer.writerow(result.data)
