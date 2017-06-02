import sys, os
import json

#This first if __name__ is needed if this file is test-run from the command line. 
# path.append needs to happen before the first from import statement
if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir,os.pardir)))


import logging
from housinginsights.sources.base import BaseApiConn

class CensusApiConn(BaseApiConn):
    """
    
    """
    def __init__(self, proxies=None):
        #baseurl not actually used since we need the _urls property to hold many urls. 
        #Needed to get call to super() to work correctly. TODO refactor so this is optional.
        baseurl = 'http://api.census.gov/data/'
        super(CensusApiConn, self).__init__(baseurl, proxies=None)
        secretsFileName =  os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.pardir,"secrets.json"))    
        self.api_keys = json.loads(open(secretsFileName).read())
        self.census_api_key = self.api_keys['census']['api_key']

        self._available_unique_data_ids = [
                        "acs5_2015",
                        "acs5_2015_moe"
                        ]

        self._urls =	{
                        "acs5_2015"     :"2015/acs5",
                        "acs5_2015_moe" :"2015/acs5"
                    	}
        self._fields = {
                        "acs5_2015"     : "NAME,B01003_001E,B25057_001E,B25058_001E,B25059_001E",
                        "acs5_2015_moe" : "NAME,B01003_001M,B25057_001M,B25058_001M,B25059_001M"
                       }	

    def get_data(self, unique_data_ids=None, sample=False, output_type = 'csv', **kwargs):
        '''
        Gets all data sources associated with this ApiConn class. 

        sample does not apply to this apiconn object because api doesn't let us request only some data. 
        '''
        if unique_data_ids == None:
            unique_data_ids = self._available_unique_data_ids

        for u in unique_data_ids:
            if (u not in self._available_unique_data_ids):
                #TODO Change this error type to a more specific one that should be handled by calling function inproduction
                #We will want the calling function to continue with other data sources instead of erroring out. 
                logging.info("  The unique_data_id '{}' is not supported by the CensusApiConn".format(u))
            else:
                result = self.get(self._urls[u], params={'key':self.census_api_key, 'get':self._fields[u], 'for': 'tract:*', 'in': 'state:11'})
                
                if result.status_code != 200:
                    err = "An error occurred during request: status {0}"
                    #TODO change this error type to be handleable by caller
                    raise Exception(err.format(result.status_code))
                
                content = result.text

                if output_type == 'stdout':
                    print(content)

                elif output_type == 'csv':
                    self.directly_to_file(content, self.output_paths[u])
                
                #Can't yield content if we get multiple sources at once
                if len(unique_data_ids) == 1:
                    return content



if __name__ == '__main__':
    
    # Pushes everything from the logger to the command line output as well.
    log_path = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir,os.pardir,"logs","sources.log"))
    logging.basicConfig(filename=log_path, level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())

    api_conn = CensusApiConn()
    unique_data_ids = None #['crime_2013']
    api_conn.get_data(unique_data_ids)
