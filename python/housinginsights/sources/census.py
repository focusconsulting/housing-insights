'''


INCOMPLETE APPROACH



See this issue: https://github.com/codefordc/housing-insights/issues/152
for some comments on latest status and next steps. 


The core method will need to be renamed to `get_data` and should have the same
method signature as others. the current opendata.py file is a good model to 
look at to provide consistent approach. 


'''









import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             os.pardir,os.pardir)))

from housinginsights.sources.base import BaseApiConn

# secrets.json, yo
census_key = os.environ.get("CENSUS_KEY")


class CensusApiConn(BaseApiConn):
    """
    Census API connector, confined to ACS5 2015 for now.

    """
    BASEURL = 'http://api.census.gov/data'

    def __init__(self, arg):
        super(CensusApiConn, self).__init__(CensusApiConn.BASEURL)
        self.arg = arg

    def getacs5(self):
        params = {'key': census_key, 'get': 'B01003_001E,B25057_001E,B25058_001E,B25059_001E', 'for': 'tract:*', 'in': 'state:11'}
        result = self.get('/2015/acs5', params=params)
        if result.status_code != 200:
            err = "An error occurred during request: status {0}"
            raise Exception(err.format(result.status_code))
        else:
            data = result
            print(data.text)


CensusApiConn('fakearg').getacs5()
