'''
    mar.py
    ------

    NOTE: This file (and API) may not be needed. A bulk download of the mar can
    be found at:

        - https://opendata.dc.gov/datasets/address-points/data
        - https://opendata.dc.gov/pages/addressing-in-dc
'''
import requests

address = '1623 16th Street NW'
BASEURL = 'http://citizenatlas.dc.gov/newwebservices/locationverifier.asmx'
params = {'f': 'json', 'address': address}

result = requests.get(BASEURL+'/verifyDCAddressThrouString2', params=params)
print(result.json()['returnDataset']['Table1'])

