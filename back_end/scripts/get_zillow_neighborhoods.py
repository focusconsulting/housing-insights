'''
A quick and dirty script used to extract lists of regions from our zillow shapefile data

Probably not needed again, relevant data has been added directly to teh code of our Cleaner. 
'''


import json

path = '../../docs/tool/data/zillow.geojson'

with open(path) as f:
    data = json.load(f)


FID_list = []
for k in data['features']:
    props_list = []
    
    props = k['properties']
    props_list.append(props['FID'])
    props_list.append(props['State'])
    props_list.append(props['Name'])
    props_list.append(props['RegionID'])
    props_list.append(props['City'])
    props_list.append(props['County'])

    FID_list.append(props['RegionID'])
    #print(props_list)

print(FID_list)