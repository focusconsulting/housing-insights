import sys
import csv
import json
import requests

###### Converts meters to miles
def getMiles(i):
    return i*0.000621371192

###### Converst miles to meters
def getMeters(i):
    return i*1609.344

def getWmataHeaders(wmata_api_key):
    return { 'api_key': wmata_api_key }

###### Gets walking distance between two locations in meters
def getWalkingDistance(srcLat, srcLon, destLat, destLon, mapbox_api_key):
    distReqCoords = srcLon + ',' + srcLat + ';' + destLon + ',' + destLat;

    mapbox_params = {'access_token':mapbox_api_key}


    #according to documentation, this doesn't work in Python SDK so switched to using REST API
    walkDistResponse = requests.get("https://api.mapbox.com/directions/v5/mapbox/walking/"+distReqCoords,
                                params=mapbox_params)
    return walkDistResponse.json()['routes'][0]['legs'][0]['distance']


###### Finds all rail stations within {radiusinmeters} from the given project. Writes to given CSV file.
def findRailStations(railStations,project,radiusinmeters,distCsvWriter, mapbox_api_key):
    lat = project['Proj_lat']
    lon = project['Proj_lon']

    for station in railStations:
        walkDist = getWalkingDistance(lat, lon, str(station['Lat']), str(station['Lon']), mapbox_api_key)
        if walkDist <= radiusinmeters:
            distCsvWriter.writerow((project['Nlihc_id'],'rail',station['Code'],"{0:.2f}".format(getMiles(walkDist))))


###### Finds all bus stations within {radiusinmeters} from the given project. Writes to given CSV file.
def findBusStations(project, radiusinmeters, distCsvWriter, wmata_api_key, mapbox_api_key):
    lat = project['Proj_lat']
    lon = project['Proj_lon']

    wmata_headers = getWmataHeaders(wmata_api_key)

    params = {'Lat': lat,
              'Lon' : lon,
              'Radius': str(radiusinmeters)}
    response = requests.get('https://api.wmata.com/Bus.svc/json/jStops',params=params, headers=wmata_headers)
    data = response.json()

    for stop in data['Stops']:
        walkDist = getWalkingDistance(lat, lon, str(stop['Lat']), str(stop['Lon']), mapbox_api_key)

        if walkDist <= radiusinmeters: #within 0.5 miles walking
            distCsvWriter.writerow((project['Nlihc_id'],'bus',stop['StopID'],"{0:.2f}".format(getMiles(walkDist))))


####### Writes rail station metadata to given CSV writer
### Returnst the railStations info...
def writeRailInfo(infoCsvWriter, wmata_api_key):

    print("Writing RAIL INFO");

    wmata_headers = getWmataHeaders(wmata_api_key)

    railResponse = requests.get("https://api.wmata.com/Rail.svc/json/jStations",headers =wmata_headers)
    railStations = railResponse.json()['Stations']

    for station in railStations:
        #delimit list of lines with colon
        lines = station['LineCode1'] #all stations have at least one line

        #there is probably a more elegant way to write this...
        if station['LineCode2'] != None:
            lines = '{}:{}'.format(lines, station['LineCode2'])

        if station['LineCode3'] != None:
            lines = '{}:{}'.format(lines, station['LineCode3'])

        if station['LineCode4'] != None:
            lines = '{}:{}'.format(lines, station['LineCode4'])

        infoCsvWriter.writerow((station['Code'],'rail',station['Name'],str(station['Lat']),
                                                        str(station['Lon']),lines))

    return railStations

####### Writes bus station metadata to given CSV writer
def writeBusInfo(infoCsvWriter, wmata_api_key):
    print("Writing BUS INFO")

    wmata_headers = getWmataHeaders(wmata_api_key)

    response = requests.get('https://api.wmata.com/Bus.svc/json/jStops', headers=wmata_headers)
    data = response.json()

    for stop in data['Stops']:

        lines = ""
        for route in stop['Routes']:
            lines = '{}:{}'.format(lines,route)
        lines = lines[1:] #take off the first :

        infoCsvWriter.writerow((stop['StopID'],'bus',stop['Name'],stop['Lat'],stop['Lon'],lines))


########### MAIN #############
def main(secretsFileName, csvInputFileName,distOutputFileName,infoOutputFileName):

    #pull API keys
    api_keys = json.loads(open(secretsFileName).read())
    wmata_api_key = api_keys['wmata']['api_key']
    mapbox_api_key = api_keys['mapbox']['public-token']

    #write out the wmata info csv
    infoOutputFile = open(infoOutputFileName, 'wt')
    infoCsvWriter = csv.writer(infoOutputFile)
    infoCsvWriter.writerow(('code_or_id','type','name','lat','lon','lines'))
    #saving railStations to compute distances from each project later in the script. reduces network calls.
    railStations = writeRailInfo(infoCsvWriter, wmata_api_key)
    writeBusInfo(infoCsvWriter, wmata_api_key)

    projectsFile = open(csvInputFileName)
    distOutputFile = open(distOutputFileName, 'wt')
    distCsvWriter = csv.writer(distOutputFile)

    reader = csv.DictReader(projectsFile)

    distCsvWriter.writerow(('Nlihc_id','type','stop_id_or_station_code','dist_in_miles'))

    numrow = 0

    for row in reader:
        radius = getMeters(0.5)

        numrow = numrow+1

        #if numrow > 1: break

        print("Processing project {} of 400ish".format(numrow))

        # find all metro stations within 0.5 miles
        print("Starting processing rail stations for {}".format(numrow))
        findRailStations(railStations,row,radius,distCsvWriter, mapbox_api_key)
        print("Completed processing rail stations for {}".format(numrow))


        # find all bus stops within 0.5 miles
        print("Starting processing bus stations for {}".format(numrow))
        findBusStations(row, radius, distCsvWriter, wmata_api_key, mapbox_api_key)
        print("Completed processing bus stations for {}".format(numrow))


if len(sys.argv) < 5:
    print("Requires 4 arguments: [csv input file] [WMATA_DIST output file] [WMATA_INFO output file] [secrets.json]")
else:
    inputFileName = sys.argv[1]
    distOutputFileName = sys.argv[2]
    infoOutputFileName = sys.argv[3]
    secretsFileName = sys.argv[4]

    print("Will read from {}".format(inputFileName))
    print("Will write WMATA_DIST table to {}".format(distOutputFileName))
    print("Will write WMATA_INFO table to {}".format(infoOutputFileName))

    main(secretsFileName, inputFileName, distOutputFileName, infoOutputFileName)
