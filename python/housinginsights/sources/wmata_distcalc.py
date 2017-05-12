import sys
import csv
import json
import requests
import os
import time
import psycopg2

class WmataApiConn():
    def __init__(self,wmata_api_key,mapbox_api_key,railStations):
        self.wmata_api_key = wmata_api_key
        self.mapbox_api_key = {'access_token':mapbox_api_key}
        self.railStations = railStations

    def getMiles(self):
        return self.miles

    def setMiles(self,miles):
        self.miles = miles
        self.meters = miles*1609.344

    def getMeters(self):
        return self.meters

    def setMeters(self, meters):
        self.meters = meters
        self.miles = meters*0.000621371192

    def setWmataApiKey(self,wmata_api_key):
        self.wmata_api_key = wmata_api_key

    def getWmataHeaders(self):
        return { 'api_key': self.wmata_api_key}

    def setMapBoxApiKey(self, mapbox_api_key):
        self.mapbox_api_key = {'access_token':mapbox_api_key}

    def getWalkingDistance(self, srcLat, srcLon, destLat, destLon):
        """Returns the walking distance in meters between two locations

           Parameters:
           srcLat - latitude for source location
           srcLon - longitude for source location
           destLat - latitude for destination location
           destLon - longitude for destination location
           mapbox_api_key - api key for mapbox REST services
           """
        distReqCoords = str(srcLon) + ',' + str(srcLat) + ';' + str(destLon) + ',' + str(destLat)

        mapbox_params = self.mapbox_api_key

        # according to documentation, this doesn't work in Python SDK so switched to using REST API
        walkDistResponse = requests.get("https://api.mapbox.com/directions/v5/mapbox/walking/" + distReqCoords,params=mapbox_params)
        if "Too Many Requests" in str(walkDistResponse.json()):
                while "Too Many Requests" in str(walkDistResponse.json()):
                        walkDistResponse = requests.get("https://api.mapbox.com/directions/v5/mapbox/walking/" + distReqCoords,params=mapbox_params)
        return walkDistResponse.json()['routes'][0]['legs'][0]['distance']


    def setProjectInfo(self,project,columns):
        for column_name in columns:
            if 'proj_lat' == column_name[0]:
                self.lat = project[columns.index(column_name)]
            elif 'proj_lon' == column_name[0]:
                self.lon = project[columns.index(column_name)]
            elif 'nlihc_id' == column_name[0]:
                self.nlihcid = project[columns.index(column_name)]

    def findRailStations(self, railStations,project,radiusinmeters,distCsvWriter):
        """Finds all the rail stations within a given distance from a given project.  Writes to the given CSV file.

        Parameters:
        railStations - json object containing all the wmata rail station information
        project - housing project object
        radiusinmeters - radius in meteres
        distCsvWriter - csvWriter for distance
        mapbox_api_key - api key for mapbox REST services
        """

        lat = self.lat
        lon = self.lon
        Nlihc_id = self.nlihcid

        for station in railStations:
            walkDist = self.getWalkingDistance(lat, lon, str(station['Lat']), str(station['Lon']))

            if walkDist <=radiusinmeters:
                distCsvWriter.writerow((Nlihc_id, 'rail', station['Code'], "{0:.2f}".format(self.getMiles())))

    def findBusStations(self, project,radiusinmeters, distCsvWriter):
        lat = self.lat
        lon = self.lon
        Nlihc_id = self.nlihcid

        wmata_headers = self.getWmataHeaders()

        params = {'Lat': lat,
                  'Lon' : lon,
                  'Radius':str(radiusinmeters)}
        response = requests.get('https://api.wmata.com/Bus.svc/json/jStops', params=params, headers=wmata_headers)
        data = response.json()

        for stop in data['Stops']:
            walkDist = self.getWalkingDistance(lat, lon, str(stop['Lat']), str(stop['Lon']))
            if walkDist <= radiusinmeters: #within 0.5 miles walking
                distCsvWriter.writerow((Nlihc_id, 'bus', stop['StopID'], "{0:.2f}".format(self.getMiles())))

class railStation():

    def __init__(self,wmata_api_key,mapbox_api_key):
        self.wmata_api_key = wmata_api_key
        self.mapbox_api_key = {'access_token':mapbox_api_key}

    def getWmataHeaders(self):
        return { 'api_key': self.wmata_api_key}

    def writeRailInfo(self, infoCsvWriter):
        """Writes all rail station data to a given CSV writer. Returns the railStations json for future processing

           Parameters:
           infoCsvWriter - csv writer
           wmata_api_key - api key for wmata REST services
           """
        print("Writing RAIL INFO")

        wmata_headers = self.getWmataHeaders()

        railResponse = requests.get("https://api.wmata.com/Rail.svc/json/jStations", headers=wmata_headers)
        railStations = railResponse.json()['Stations']

        for station in railStations:
            #delimit list of lines with colon
            lines = station["LineCode1"] #there is always at least one station
            for line_code in ["LineCode2", "LineCode3", "LineCode4"]:
                if station[line_code] != None:
                    lines += ":" + station[line_code]
            infoCsvWriter.writerow((station['Code'], 'rail',station['Name'],str(station['Lat']), str(station['Lon']),lines))

        return railStations

    def writeBusInfo(self, infoCsvWriter):
        """Writes all bus station data to a given CSV writer.

            Parameters:
            infoCsvWriter - csv writer
            wmata_api_key - api key for wmata REST services
            """

        print("Writing BUS INFO")

        wmata_headers = self.getWmataHeaders()

        response = requests.get('https://api.wmata.com/Bus.svc/json/jStops', headers=wmata_headers)
        data = response.json()

        for stop in data['Stops']:

            lines = ""
            for route in stop['Routes']:
                lines = '{}:{}'.format(lines, route)
            lines = lines[1:] #take off the first :

            infoCsvWriter.writerow((stop['StopID'], 'bus', stop['Name'], stop['Lat'],stop['Lon'], lines)) #, stop_id_or_station_code))
    

def main(secretsFileName, distOutputFileName,infoOutputFileName):
    """Writes two csvs: 1 for general bus/rail info, 1 with distances to wmata for projects

   Parameters:
   secretsFileName - json file name that contains various api keys
   csvInputFileName - csv file with project information
   distOutputFileName - csv file to output to for calculated metro distances for each project
   infoOutputFileName - cvs file for general bus & rail info for each wmata station
   """

    try:
        conn = psycopg2.connect("dbname='housinginsights_docker' user='codefordc' host='192.168.99.100' password='codefordc'")
        print("Connected to Housing Insights database")
    except:
        print("I am unable to connect to the database")

    cur = conn.cursor()
    cur.execute("""select column_name from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME='project'""")
    columns = cur.fetchall()
    cur.execute("""select * from project;""")
    rows = cur.fetchall()

    #pull API keys
    api_keys = json.loads(open(secretsFileName).read())
    wmata_api_key = api_keys['wmata']['api_key']
    mapbox_api_key = api_keys['mapbox']['public-token']

    #write out the wmata info csv
    infoOutputFile = open(infoOutputFileName, 'wt')
    infoCsvWriter = csv.writer(infoOutputFile)
    infoCsvWriter.writerow(('code_or_id','type','name','lat','lon','lines','stop_id_or_station_code'))
    #saving railStations to compute distances from each project later in the script. reduces network calls.

    #Creat railStation object
    newRailStations = railStation(wmata_api_key,mapbox_api_key)
    railStations = newRailStations.writeRailInfo(infoCsvWriter)
    newRailStations.writeBusInfo(infoCsvWriter)

    #projectsFile = open(csvInputFileName)
    distOutputFile = open(distOutputFileName, 'wt')
    distCsvWriter = csv.writer(distOutputFile)

    #reader = csv.DictReader(projectsFile)

    distCsvWriter.writerow(('Nlihc_id','type','stop_id_or_station_code','dist_in_miles'))

    numrow = 0

    for row in rows: #reader:
        newEntry = WmataApiConn(wmata_api_key,mapbox_api_key,railStations)
        newEntry.setMiles(0.5)
        radius = newEntry.getMeters()
        newEntry.setProjectInfo(row,columns)

        numrow = numrow+1

        #if numrow > 1: break

        print("Processing project {} of 400ish".format(numrow))

        # find all metro stations within 0.5 miles
        print("Starting processing rail stations for {}".format(numrow))
        newEntry.findRailStations(railStations,row,radius,distCsvWriter)
        print("Completed processing rail stations for {}".format(numrow))


        # find all bus stops within 0.5 miles
        print("Starting processing bus stations for {}".format(numrow))
        newEntry.findBusStations(row, radius, distCsvWriter)
        print("Completed processing bus stations for {}".format(numrow))

if __name__ == '__main__':
#    if len(sys.argv) < 1:
#        print("Requires 1 arguments: [csv input file]")
#    else:
#    inputFileName = sys.argv[1]
    secretsFileName = "../secrets.json"

    now = time.strftime("%Y%m%d")
    outputDir = "../../../data/raw/wmata/" + now

    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    distOutputFileName = outputDir + "/dist.csv"
    infoOutputFileName = outputDir + "/wmatainfo.csv"


#    print("Will read from {}".format(inputFileName))
    print("Will write WMATA_DIST table to {}".format(distOutputFileName))
    print("Will write WMATA_INFO table to {}".format(infoOutputFileName))

    main(secretsFileName, distOutputFileName, infoOutputFileName)
