'''
    dhcd.py
    -------

    This file collects Projects and Properties from the
    DC Department of Housing and Community Development.

    TO-DO: Establish the outputs needed from this data, and clean some of the
    raw data in this file.

    The data is used to create the projects and subsidies tables.

    This data is combined with Projects.csv and Subsidies
    from the Preservation Catalog (provided manually - on the s3).

'''

import requests
import pandas as pd
from xml.etree import ElementTree
from xmljson import parker as xml_to_json

def get_table(table, params):
    '''Gets the XML data for a given table alias.'''
    r = requests.get(f'https://octo.quickbase.com/db/{table}', params=params)
    print(table, r)
    return pd.DataFrame(xml_to_json.data(ElementTree.fromstring(r.text))['record'])

# Gets default fields for 'Projects'.
projects = get_table('bit4krbdh', {'a': 'API_DoQuery', 'query': '{\'1\'.XEX.\'0\'}'})

# Gets all fields for 'Properties'.
properties = get_table('bi4xqgzv4', {'a': 'API_DoQuery', 'query': '{\'1\'.XEX.\'0\'}', 'clist': 'a', 'slist': '3'})
