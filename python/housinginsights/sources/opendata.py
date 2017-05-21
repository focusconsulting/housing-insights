from requests

from housinginsights.sources.base import BaseApiConn

class OpenDataApiConn(BaseApiConn):
    """
    Opendata.dc.gov provides multiple data sets that we need. They provide an api endpoint for each data file that we need already in .csv format\
    To add new datasource, go to the opendata.dc.gov site.
    In the API tab, change the URL in geojson to end in .csv
    Then follow the example in get_tax_public_extracts ticket to get the url and save to file.
    """
    def __init__(self, baseurl, proxies=None):
        """
        add properties where to save each data type
        """
        super(OpenDataApiConn, self).__init__(baseurl, proxies=None)
        self.tax_public_extracts_tickets_path = '/data/raw/tax'
        self.building_permits_path = '/data/raw/building-permits-in-2016'

    # Initialize a list to store all the get data functions.
    get_opendatas = []

    # This function is used as a decorator
    def opendatas(self,get_data_func):
        get_datas.append(get_opendata_func)
        return get_opendata_func
    
    @opendatas
    def get_tax_public_extracts_tickets(self,save_name='integrated-tax-system-public-extract-facts.csv'):
        """
        Download csv folder and save to appropriate subfolder
        tax public extracts tickets 
        http://opendata.dc.gov/datasets/integrated-tax-system-public-extract-facts
        """
        url = 'https://opendata.arcgis.com/datasets/014f4b4f94ea461498bfeba877d92319_56.csv'
        resp = requests.get(url)
        url_save_name = os.path.join(self.data_type_save_place, save_name)
        f = open(url_save_name, 'wb')
        f.write(resp.content)
        f.close()

    @opendatas
    def get_building_permits_2016(self,save_name='building-permits-in-2016.csv'):
        """
        Download csv folder and save to appropriate subfolder
        building permits 2016 
        http://opendata.dc.gov/datasets/building-permits-in-2016
        """
        url='https://opendata.arcgis.com/datasets/5d14ae7dcd1544878c54e61edda489c3_24.csv'
        resp = requests.get(url)
        url_save_name = os.path.join(self.data_type_save_place, save_name)
        f = open(url_save_name, 'wb')
        f.write(resp.content)
        f.close()
        
    def get_data(self):
        # get all the data
        # Call all the functions with the opendatas decorators
        for get_current_opendata in get_opendatas:
            get_current_opendata(save_name)

