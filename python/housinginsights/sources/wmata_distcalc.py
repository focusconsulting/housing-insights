import sys
import csv
import json
import requests
import os
import time
#import psycopg2
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir)))
from housinginsights.sources.base import BaseApiConn
import housinginsights.tools.dbtools as dbtools
import sqlalchemy
#sys.path.insert(0, '../tools/dbtools.py')
#import tools.dbtools

class WmataApiConn(BaseApiConn):

    def __init__(self):

        secretsFileName = "../secrets.json"

        now = time.strftime("%Y%m%d")
        outputDir = "../../../data/raw/wmata/" + now

        if not os.path.exists(outputDir):
            os.makedirs(outputDir)

        self.distOutputFileName = outputDir + "/dist.csv"
        self.infoOutputFileName = outputDir + "/wmatainfo.csv"

        print("Will write WMATA_DIST table to {}".format(self.distOutputFileName))
        print("Will write WMATA_INFO table to {}".format(self.infoOutputFileName))

        #pull API keys
        self.api_keys = json.loads(open(secretsFileName).read())
        self.wmata_api_key = self.api_keys['wmata']['api_key']
        self.mapbox_api_key = {'access_token':self.api_keys['mapbox']['public-token']}

        #write out the wmata info csv
        self.infoOutputFile = open(self.infoOutputFileName, 'wt')
        self.infoCsvWriter = csv.writer(self.infoOutputFile)
        self.infoHeaders = ('code_or_id','type','name','lat','lon','lines','stop_id_or_station_code')
        self.infoCsvWriter.writerow(('code_or_id','type','name','lat','lon','lines','stop_id_or_station_code'))

        #write out hte dist.csv file
        self.distOutputFile = open(self.distOutputFileName, 'wt')
        self.distCsvWriter = csv.writer(self.distOutputFile)
        self.distHeader = ('Nlihc_id','type','stop_id_or_station_code','dist_in_miles')
        self.distCsvWriter.writerow(('Nlihc_id','type','stop_id_or_station_code','dist_in_miles'))
        
        #Creat railStation object
        self.railStations = self.writeRailInfo(self.infoCsvWriter)
        self.writeBusInfo(self.infoCsvWriter)

    def getData(self):
        try:
            engine = dbtools.get_database_engine('docker_database')
            conn = dbtools.get_database_connection('docker_database') 
            print("Connected to Housing Insights database")
            columnset = conn.execute('select column_name from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME=\'project\'')
            rows = conn.execute('select * from project')
        except Exception as e:
            print(e)
            print("I am unable to connect to the database")

        columns = []
        for c in columnset:
            columns.append(c)

        numrow = 0

        for row in rows: #reader:
            radius = self.getMeters(0.5)
            self.setProjectInfo(row,columns)

            numrow = numrow+1

            print("Processing project {} of 400ish".format(numrow))

            # find all metro stations within 0.5 miles
            print("Starting processing rail stations for {}".format(numrow))
            self.findRailStations(self.railStations,row,radius,self.distCsvWriter)
            print("Completed processing rail stations for {}".format(numrow))

            # find all bus stops within 0.5 miles
            print("Starting processing bus stations for {}".format(numrow))
            self.findBusStations(row, radius, self.distCsvWriter)
            print("Completed processing bus stations for {}".format(numrow))

    def getMeters(self,miles):
        self.miles = miles
        self.meters = miles*1609.344
        return self.meters

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
        time.sleep(0.8)
        if "Too Many Requests" in str(walkDistResponse.json()):
                i = 0
                while "Too Many Requests" in str(walkDistResponse.json()) and i < 10:
                    walkDistResponse = requests.get("https://api.mapbox.com/directions/v5/mapbox/walking/" + distReqCoords,params=mapbox_params)
                    i = i + 1
                    if i == 10:
                        raise Exception('This is some exception to be defined later')
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
                #railData.append([Nlihc_id, 'rail', station['Code'], "{0:.2f}".format(self.miles)])
                distCsvWriter.writerow([Nlihc_id, 'rail', station['Code'], "{0:.2f}".format(self.miles)])

        #self.result_to_csv(distHeader,railData,self.distOutputFileName)

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
                distCsvWriter.writerow([Nlihc_id, 'bus', stop['StopID'], "{0:.2f}".format(self.miles)])

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

            infoCsvWriter.writerow((stop['StopID'], 'bus', stop['Name'], stop['Lat'],stop['Lon'], lines))

#if __name__ == '__main__':

#    testClass = WmataApiConn()
#    testClass.getData()
    