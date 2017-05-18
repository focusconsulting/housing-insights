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
        self.outputDir = "../../../data/raw/wmata/" + now

        if not os.path.exists(self.outputDir):
            os.makedirs(self.outputDir)

        #pull API keys
        self.api_keys = json.loads(open(secretsFileName).read())
        self.wmata_api_key = self.api_keys['wmata']['api_key']
        self.mapbox_api_key = {'access_token':self.api_keys['mapbox']['public-token']}

    # def get_data(self):
    #     self.get_rail_stations
    #     self.get_bus_stations
    #     self.get_station_walking_distances

    def get_data(self):

        self.distOutputFileName = self.outputDir + "/dist.csv"
        self.infoOutputFileName = self.outputDir + "/wmatainfo.csv"

        print("Will write WMATA_DIST table to {}".format(self.distOutputFileName))
        print("Will write WMATA_INFO table to {}".format(self.infoOutputFileName))

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
        self.railStations = self._get_all_rail_stations(self.infoCsvWriter)
        self._get_all_bus_stations(self.infoCsvWriter)

        try:
            engine = dbtools.get_database_engine('local_database')
            conn = dbtools.get_database_connection('local_database') 
            print("Connected to Housing Insights database")
            columnset = conn.execute('select column_name from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME=\'project\'')
            rows = conn.execute('select * from project limit 1')
            conn.close()
            engine.dispose()
        except Exception as e:
            print(e)
            print("I am unable to connect to the database")

        columns = []
        for c in columnset:
            columns.append(c)

        numrow = 0
        total_rows = rows.rowcount

        for row in rows: #reader:
            radius = self._get_meters(0.5)
            self._set_project_info(row,columns)

            numrow = numrow+1

            print("Processing project {} of {}".format(numrow,total_rows))

            # find all metro stations within 0.5 miles
            print("Starting processing rail stations for {}".format(numrow))
            self._find_rail_stations(self.railStations,row,radius,self.distCsvWriter)
            print("Completed processing rail stations for {}".format(numrow))

            # find all bus stops within 0.5 miles
            print("Starting processing bus stations for {}".format(numrow))
            self._find_bus_stations(row, radius, self.distCsvWriter)
            print("Completed processing bus stations for {}".format(numrow))

    def _get_meters(self,miles):
        self.miles = miles
        self.meters = miles*1609.344
        return self.meters

    def _set_wmata_api_key(self,wmata_api_key):
        self.wmata_api_key = wmata_api_key

    def _get_wmata_headers(self):
        return { 'api_key': self.wmata_api_key}

    def _set_mapbox_api_key(self, mapbox_api_key):
        self.mapbox_api_key = {'access_token':mapbox_api_key}

    def _get_walking_distance(self, srcLat, srcLon, destLat, destLon):
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
                    time.sleep(0.8)
                    if i == 10:
                        raise Exception('This is some exception to be defined later')
        return walkDistResponse.json()['routes'][0]['legs'][0]['distance']


    def _set_project_info(self,project,columns):
        for column_name in columns:
            if 'proj_lat' == column_name[0]:
                self.lat = project[columns.index(column_name)]
            elif 'proj_lon' == column_name[0]:
                self.lon = project[columns.index(column_name)]
            elif 'nlihc_id' == column_name[0]:
                self.nlihcid = project[columns.index(column_name)]

    def _find_rail_stations(self, railStations,project,radiusinmeters,distCsvWriter):
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
            walkDist = self._get_walking_distance(lat, lon, str(station['Lat']), str(station['Lon']))

            if walkDist <=radiusinmeters:
                #railData.append([Nlihc_id, 'rail', station['Code'], "{0:.2f}".format(self.miles)])
                distCsvWriter.writerow([Nlihc_id, 'rail', station['Code'], "{0:.2f}".format(self.miles)])

        #self.result_to_csv(distHeader,railData,self.distOutputFileName)

    def _find_bus_stations(self, project,radiusinmeters, distCsvWriter):
        lat = self.lat
        lon = self.lon
        Nlihc_id = self.nlihcid

        wmata_headers = self._get_wmata_headers()

        params = {'Lat': lat,
                  'Lon' : lon,
                  'Radius':str(radiusinmeters)}
        response = requests.get('https://api.wmata.com/Bus.svc/json/jStops', params=params, headers=wmata_headers)
        data = response.json()

        for stop in data['Stops']:
            walkDist = self._get_walking_distance(lat, lon, str(stop['Lat']), str(stop['Lon']))

            if walkDist <= radiusinmeters: #within 0.5 miles walking
                distCsvWriter.writerow([Nlihc_id, 'bus', stop['StopID'], "{0:.2f}".format(self.miles)])

    def _get_all_rail_stations(self, infoCsvWriter):
        """Writes all rail station data to a given CSV writer. Returns the railStations json for future processing

           Parameters:
           infoCsvWriter - csv writer
           wmata_api_key - api key for wmata REST services
           """
        print("Writing RAIL INFO")

        wmata_headers = self._get_wmata_headers()

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

    def _get_all_bus_stations(self, infoCsvWriter):
        """Writes all bus station data to a given CSV writer.

            Parameters:
            infoCsvWriter - csv writer
            wmata_api_key - api key for wmata REST services
            """

        print("Writing BUS INFO")

        wmata_headers = self._get_wmata_headers()

        response = requests.get('https://api.wmata.com/Bus.svc/json/jStops', headers=wmata_headers)
        busStops = response.json()['Stops']

        for stop in busStops:

            lines = ""
            for route in stop['Routes']:
                lines = '{}:{}'.format(lines, route)
            lines = lines[1:] #take off the first :

            infoCsvWriter.writerow((stop['StopID'], 'bus', stop['Name'], stop['Lat'],stop['Lon'], lines))

        return busStops

if __name__ == '__main__':

    testClass = WmataApiConn()
    testClass.get_data()
    