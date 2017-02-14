import sys
import csv
import requests

#TODO replace these with code4dc keys
WMATA_HEADERS = {'api_key': ''}
MAPBOX_PARAMS = {'access_token': ''}

###### Converts meters to miles
def getMiles(i):
    return i*0.000621371192

###### Converst miles to meters
def getMeters(i):
    return i*1609.344

###### Gets walking distance between two locations in meters
def getWalkingDistance(srcLat, srcLon, destLat, destLon):
    distReqCoords = srcLon + ',' + srcLat + ';' + destLon + ',' + destLat;

    #according to documentation, this doesn't work in Python SDK so switched to using REST API
    walkDistResponse = requests.get("https://api.mapbox.com/directions/v5/mapbox/walking/"+distReqCoords,
                                params=MAPBOX_PARAMS)
    return walkDistResponse.json()['routes'][0]['legs'][0]['distance']


###### Finds all rail stations within {radiusinmeters} from the given project. Writes to given CSV file.
def findRailStations(railStations,project,radiusinmeters,distCsvWriter):
    lat = project['Proj_lat']
    lon = project['Proj_lon']

    for station in railStations:
        walkDist = getWalkingDistance(lat, lon, str(station['Lat']), str(station['Lon']))
        if walkDist <= radiusinmeters:
            distCsvWriter.writerow((project['Nlihc_id'],'rail',station['Code'],getMiles(walkDist)))


###### Finds all bus stations within {radiusinmeters} from the given project. Writes to given CSV file.
def findBusStations(project, radiusinmeters, distCsvWriter):
    lat = project['Proj_lat']
    lon = project['Proj_lon']

    params = {'Lat': lat,
              'Lon' : lon,
              'Radius': str(radiusinmeters)}
    response = requests.get('https://api.wmata.com/Bus.svc/json/jStops',params=params, headers=WMATA_HEADERS)
    data = response.json()

    for stop in data['Stops']:
        walkDist = getWalkingDistance(lat, lon, str(stop['Lat']), str(stop['Lon']))

        if walkDist <= radiusinmeters: #within 0.5 miles walking
            distCsvWriter.writerow((project['Nlihc_id'],'bus',stop['StopID'],getMiles(walkDist)))


####### Writes rail station metadata to given CSV writer
def writeRailInfo(railStations, infoCsvWriter):

    print("Writing RAIL INFO");

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

        infoCsvWriter.writerow((station['Code'],station['Name'],str(station['Lat']),
                                                        str(station['Lon']),lines))
####### Writes bus station metadata to given CSV writer
def writeBusInfo(infoCsvWriter):
    print("Writing BUS INFO")

    response = requests.get('https://api.wmata.com/Bus.svc/json/jStops', headers=WMATA_HEADERS)
    data = response.json()

    for stop in data['Stops']:

        lines = ""
        for route in stop['Routes']:
            lines = '{}:{}'.format(lines,route)
        lines = lines[1:] #take off the first :

        infoCsvWriter.writerow((stop['StopID'],stop['Name'],stop['Lat'],stop['Lon'],lines))



########### MAIN #############
def main(csvInputFileName,distOutputFileName,infoOutputFileName):

    projectsFile = open(csvInputFileName)
    distOutputFile = open(distOutputFileName, 'wt')
    distCsvWriter = csv.writer(distOutputFile)

    infoOutputFile = open(infoOutputFileName, 'wt')
    infoCsvWriter = csv.writer(infoOutputFile)

    reader = csv.DictReader(projectsFile)

    numrow = 0

    #print headers
    distCsvWriter.writerow(('Nlihc_id','type','stop_id_or_station_code','dist_in_miles'))
    infoCsvWriter.writerow(('code_or_id','type','name','lat','lon','lines'))

    railResponse = requests.get("https://api.wmata.com/Rail.svc/json/jStations",headers =WMATA_HEADERS)
    railStations = railResponse.json()['Stations']
    writeRailInfo(railStations, infoCsvWriter)
    writeBusInfo(infoCsvWriter)

    for row in reader:
        radius = getMeters(0.5)

        numrow = numrow+1
        print("Processing project {} of 400ish".format(numrow))

        # find all metro stations within 0.5 miles
        print("Starting processing rail stations for {}".format(numrow))
        findRailStations(railStations,row,radius,distCsvWriter)
        print("Completed processing rail stations for {}".format(numrow))


        # find all bus stops within 0.5 miles
        print("Starting processing bus stations for {}".format(numrow))
        findBusStations(row, radius, distCsvWriter)
        print("Completed processing bus stations for {}".format(numrow))


if len(sys.argv) < 4:
    print("Requires 3 arguments: [csv input file] [WMATA_DIST output file] [WMATA_INFO output file]")
else:
    inputFileName = sys.argv[1]
    distOutputFileName = sys.argv[2]
    infoOutputFileName = sys.argv[3]
    print("Will read from {}".format(inputFileName))
    print("Will write WMATA_DIST table to {}".format(distOutputFileName))
    print("Will write WMATA_INFO table to {}".format(infoOutputFileName))

    main(inputFileName, distOutputFileName, infoOutputFileName)
