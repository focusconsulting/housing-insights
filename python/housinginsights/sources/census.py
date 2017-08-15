import sys, os
import json

#This first if __name__ is needed if this file is test-run from the command line. 
# path.append needs to happen before the first from import statement
if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir,os.pardir)))


from housinginsights.sources.base import BaseApiConn
from housinginsights.tools.logger import HILogger

logger = HILogger(name=__file__, logfile="sources.log", level=10)

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
                        "acs5_2009",
                        "acs5_2010",
                        "acs5_2011",
                        "acs5_2012",
                        "acs5_2013",
                        "acs5_2014",
                        "acs5_2015",
                        "acs5_2009_moe",
                        "acs5_2010_moe",
                        "acs5_2011_moe",
                        "acs5_2012_moe",
                        "acs5_2013_moe",
                        "acs5_2014_moe",
                        "acs5_2015_moe"
                        ]

        self._urls =	{
                        "acs5_2009"     :"2009/acs5",
                        "acs5_2010"     :"2010/acs5",
                        "acs5_2011"     :"2011/acs5",
                        "acs5_2012"     :"2012/acs5",
                        "acs5_2013"     :"2013/acs5",
                        "acs5_2014"     :"2014/acs5",
                        "acs5_2015"     :"2015/acs5",
                        "acs5_2009_moe" :"2009/acs5",
                        "acs5_2010_moe" :"2010/acs5",
                        "acs5_2011_moe" :"2011/acs5",
                        "acs5_2012_moe" :"2012/acs5",
                        "acs5_2013_moe" :"2013/acs5",
                        "acs5_2014_moe" :"2014/acs5",
                        "acs5_2015_moe" :"2015/acs5"
                    	}

        #TODO this data cannot be loaded into the database as-is because the column names vary between years. 
        #Also, it is difficult to see the changes in which columns are included each year
        #Should reformat how our desired fields are coded in and how they are mapped to column names in the CSV file
        self._fields = {
                        "acs5_2009"     : "NAME,B01003_001E,B25057_001E,B25058_001E,B25059_001E,B02001_003E,B19025_001E,B16008_019E,B09002_015E,B17001_002E",
                        "acs5_2010"     : "NAME,B01003_001E,B25057_001E,B25058_001E,B25059_001E,B02001_003E,B19025_001E,B16008_019E,B09002_015E,B17001_002E",
                        "acs5_2011"     : "NAME,B01003_001E,B25057_001E,B25058_001E,B25059_001E,B02001_003E,B19025_001E,B23025_002E,B16008_019E,B09002_015E,B17001_002E",
                        "acs5_2012"     : "NAME,B01003_001E,B25057_001E,B25058_001E,B25059_001E,B02001_003E,B19025_001E,B23025_002E,B16008_019E,B09002_015E,B17001_002E",
                        "acs5_2013"     : "NAME,B01003_001E,B25057_001E,B25058_001E,B25059_001E,B02001_003E,B17020_002E,B19025_001E,B23025_002E,B16008_019E,B09002_015E",
                        "acs5_2014"     : "NAME,B01003_001E,B25057_001E,B25058_001E,B25059_001E,B02001_003E,B17020_002E,B19025_001E,B23025_002E,B16008_019E,B09002_015E", 
                        "acs5_2015"     : "NAME,B01003_001E,B25057_001E,B25058_001E,B25059_001E,B02001_003E,B17020_002E,B19025_001E,B23025_002E,B16008_019E,B09002_015E",
                        "acs5_2009_moe" : "NAME,B01003_001M,B25057_001M,B25058_001M,B25059_001M,B02001_003M,B19025_001M,B16008_019M,B09002_015M,B17001_002M",
                        "acs5_2010_moe" : "NAME,B01003_001M,B25057_001M,B25058_001M,B25059_001M,B02001_003M,B19025_001M,B16008_019M,B09002_015M,B17001_002M",
                        "acs5_2011_moe" : "NAME,B01003_001M,B25057_001M,B25058_001M,B25059_001M,B02001_003M,B19025_001M,B23025_002M,B16008_019M,B09002_015M,B17001_002M",
                        "acs5_2012_moe" : "NAME,B01003_001M,B25057_001M,B25058_001M,B25059_001M,B02001_003M,B19025_001M,B23025_002M,B16008_019M,B09002_015M,B17001_002M",
                        "acs5_2013_moe" : "NAME,B01003_001M,B25057_001M,B25058_001M,B25059_001M,B02001_003M,B17020_002M,B19025_001M,B23025_002M,B16008_019M,B09002_015M",
                        "acs5_2014_moe" : "NAME,B01003_001M,B25057_001M,B25058_001M,B25059_001M,B02001_003M,B17020_002M,B19025_001M,B23025_002M,B16008_019M,B09002_015M",
                        "acs5_2015_moe" : "NAME,B01003_001M,B25057_001M,B25058_001M,B25059_001M,B02001_003M,B17020_002M,B19025_001M,B23025_002M,B16008_019M,B09002_015M"
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
                logger.info("  The unique_data_id '%s' is not supported by the CensusApiConn", u)
            else:
                result = self.get(self._urls[u], params={'key':self.census_api_key, 'get':self._fields[u], 'for': 'tract:*', 'in': 'state:11'})

                if result.status_code != 200:
                    err = "An error occurred during request: status {0}".format(result.status_code)
                    logger.error(err)
                    #TODO change this error type to be handleable by caller
                    raise Exception(err)

                content = result.text

                if output_type == 'stdout':
                    print(content)

                elif output_type == 'csv':
                    jsondata=json.loads(content)
                    self.result_to_csv(jsondata[0], jsondata[1:],  self.output_paths[u])

                #Can't yield content if we get multiple sources at once
                if len(unique_data_ids) == 1:
                    return content


                
if __name__ == '__main__':

    # Pushes everything from the logger to the command line output as well.
    
    api_conn = CensusApiConn()
    unique_data_ids = None 
    api_conn.get_data(unique_data_ids)
