'''
    mar.py
    ------

    Testing the mar data loading.
'''
import requests

address = '1623 16th Street NW'
BASEURL = 'http://citizenatlas.dc.gov/newwebservices/locationverifier.asmx'
params = {'f': 'json', 'address': address}

result = requests.get(BASEURL+'/verifyDCAddressThrouString2', params=params)
print(result.json()['returnDataset']['Table1'])

