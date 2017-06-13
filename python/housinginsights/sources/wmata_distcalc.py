import sys
import csv
import json
import requests
import os
import time
import time
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir)))
from housinginsights.sources.base import BaseApiConn
import housinginsights.tools.dbtools as dbtools
import sqlalchemy

class WmataApiConn(BaseApiConn):

    def __init__(self, proxies=None, use_cached_distance=True):
        baseurl=None #more than one, so calls to self.get() must pass whole url
        super().__init__(baseurl, proxies=None)

        self.meters_per_mile = 1609.344
        self.use_cached_distance = use_cached_distance

        #pull API keys
        secretsFileName =  os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.pardir,"secrets.json"))
        self.api_keys = json.loads(open(secretsFileName).read())
        self.wmata_api_key = self.api_keys['wmata']['api_key']
        self.mapbox_api_key = {'access_token':self.api_keys['mapbox']['public-token']}

        self._available_unique_data_ids = [
                        "wmata_stops",
                        "wmata_dist"]


    def get_data(self,unique_data_ids=None, sample=False, output_type ='csv',db='local_database', **kwargs):
        if unique_data_ids == None:
            unique_data_ids = self._available_unique_data_ids

        for u in unique_data_ids:
            if u == 'wmata_stops':
                self.get_stops(unique_data_ids=['wmata_stops'],sample=sample,output_type=output_type)
            elif u == 'wmata_dist':
                self.get_dist(unique_data_ids=['wmata_dist'],sample=sample,output_type=output_type,db=db)
            else:
                logging.info("  unique_data_id '{}' not supported by the WmataApiConn".format(u))

    def get_stops(self, unique_data_ids=None, sample=False, output_type ='csv'):

        #Variable to hold both bus and rail stops data while accessing the data
        self.stopsOutput = []
        self.stopsHeader = ('stop_id_or_station_code','type','name','latitude','longitude','lines')

        if 'wmata_stops' in unique_data_ids:
            u = 'wmata_stops'
            #Create objects and write to table
            self.railStations = self._get_all_rail_stations()
            self.busStations = self._get_all_bus_stations()

            if ( output_type == 'csv'):
                self._array_to_csv(self.stopsHeader,self.stopsOutput, self.output_paths[u])

            elif ( output_type == 'stdout'):
                logging.info("==========================================================================\n")
                logging.info(self.stopsHeader)
                logging.info("--------------------------------------------------------------------------\n")
                for line in self.stopsOutput:
                    logging.info(line)

            else:
                self._array_to_csv(self.stopsHeader,self.stopsOutput,output_type)
        else:
            #Not an id supported by this method
            pass

    def get_dist(self, unique_data_ids=None, sample=False, output_type='csv',db='local_database'):

        if 'wmata_dist' in unique_data_ids:
            u = 'wmata_dist'
            #Variable to hold data until written to file
            self.distOutput = []
            self.distHeader = ('nlihc_id','type','stop_id_or_station_code','dist_in_miles','crow_distance','building_lat','building_lon','stop_or_station_lat','stop_or_station_lon')


            #First, find which projects we should be calculating from
            try:
                #Configure the connection
                engine = dbtools.get_database_engine(db)
                conn = dbtools.get_database_connection(db)
                logging.info("  Connected to Housing Insights database")
                columnset = conn.execute('select column_name from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME=\'project\'')

                #Get the rows
                proj_query = 'select * from project'
                if sample==True:
                    proj_query = proj_query + " limit 1"
                rows = conn.execute(proj_query)

                conn.close()
                engine.dispose()
            except Exception as e:
                logging.warning(e)
                logging.warning("I am unable to connect to the database")

            columns = []
            for c in columnset:
                columns.append(c)

            numrow = 0
            total_rows = rows.rowcount
            logging.info("  Total rows: {}".format(total_rows))

            #Get the rail stations once (no option to only get closest ones provided by wmata)
            wmata_headers = self._get_wmata_headers()
            railResponse = requests.get("https://api.wmata.com/Rail.svc/json/jStations", headers=wmata_headers)
            self.railStations = railResponse.json()['Stations']

            #for every project, get nearby stations and walking distance
            for idx, row in enumerate(rows):
                radius = self._get_meters(0.5)

                project_details = self._get_project_info(row,columns)
                lat = project_details['lat']
                lon = project_details['lon']

                if lat == None or lon == None:
                    logging.warning("  Lat or Lon not available for project {}".format(project_details['nlihcid']))
                    
                if lat != None and lon != None:
                    logging.info("  Processing project {} of {}".format(numrow,total_rows))

                    # find all metro stations within 0.5 miles
                    logging.info("  Starting processing rail stations for {}".format(project_details['nlihcid']))
                    self._find_rail_stations(self.railStations,project_details,radius,sample=sample,db=db)
                    logging.info("  Completed processing rail stations for project id {}".format(project_details['nlihcid']))

                    # find all bus stops within 0.5 miles
                    logging.info("  Starting processing bus stations for project id {}".format(project_details['nlihcid']))
                    self._find_bus_stations(project_details, radius,sample=sample,db=db)
                    logging.info("  Completed processing bus stations for project id {}".format(project_details['nlihcid']))

            #Save the data
            if ( output_type == 'csv'):
                self._array_to_csv(self.distHeader, self.distOutput, self.output_paths[u])

            elif ( output_type == 'stdout'):
                logging.info("==========================================================================\n")
                logging.info(self.distHeader)
                logging.info("==========================================================================\n")
                for line in self.distOutput:
                    logging.info(line)

            else:
                self._array_to_csv(self.distHeader, self.distOutput,output_type)
        else:
            #not a unique data id supported by this class
            pass


    def _get_all_rail_stations(self):
        """Writes all rail station data to a given CSV writer. Returns the railStations json for future processing

           Parameters:
           infoCsvWriter - csv writer
           wmata_api_key - api key for wmata REST services
           """
        logging.info("Writing RAIL stops")

        wmata_headers = self._get_wmata_headers()

        railResponse = requests.get("https://api.wmata.com/Rail.svc/json/jStations", headers=wmata_headers)
        railStations = railResponse.json()['Stations']

        for station in railStations:
            #delimit list of lines with colon
            lines = station["LineCode1"] #there is always at least one station
            for line_code in ["LineCode2", "LineCode3", "LineCode4"]:
                if station[line_code] != None:
                    lines += ":" + station[line_code]
            data = [ station['Code'], 'rail',station['Name'],str(station['Lat']), str(station['Lon']),lines ]
            self.stopsOutput.append(data)
            #infoCsvWriter.writerow((station['Code'], 'rail',station['Name'],str(station['Lat']), str(station['Lon']),lines))

        return railStations

    def _get_all_bus_stations(self):
        """Writes all bus station data to a given CSV writer.

            Parameters:
            infoCsvWriter - csv writer
            wmata_api_key - api key for wmata REST services
            """

        logging.info("Writing BUS stops")

        wmata_headers = self._get_wmata_headers()

        response = requests.get('https://api.wmata.com/Bus.svc/json/jStops', headers=wmata_headers)
        busStops = response.json()['Stops']

        for stop in busStops:

            lines = ""
            for route in stop['Routes']:
                lines = '{}:{}'.format(lines, route)
            lines = lines[1:] #take off the first :

            data = [stop['StopID'], 'bus', stop['Name'], stop['Lat'],stop['Lon'], lines]
            self.stopsOutput.append(data)
            #infoCsvWriter.writerow((stop['StopID'], 'bus', stop['Name'], stop['Lat'],stop['Lon'], lines))

        return busStops

    def _get_meters(self,miles):
        self.miles = miles
        self.meters = miles*self.meters_per_mile
        return self.meters

    def _set_wmata_api_key(self,wmata_api_key):
        self.wmata_api_key = wmata_api_key

    def _get_wmata_headers(self):
        return { 'api_key': self.wmata_api_key}

    def _set_mapbox_api_key(self, mapbox_api_key):
        self.mapbox_api_key = {'access_token':mapbox_api_key}

    def _get_walking_distance(self, srcLat, srcLon, destLat, destLon,db='local_database'):
        """Returns the walking distance in meters between two locations

           Parameters:
           srcLat - latitude for source location
           srcLon - longitude for source location
           destLat - latitude for destination location
           destLon - longitude for destination location
           mapbox_api_key - api key for mapbox REST services
           """

        if self.use_cached_distance == True:
            try:
                #Configure the connection
                engine = dbtools.get_database_engine(db)
                conn = dbtools.get_database_connection(db)
                logging.info("  Connected to Housing Insights database")

                #Pull columns to see if the database has updated columns in wmata_dist
                columnset = conn.execute('select column_name from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME=\'wmata_dist\'')
                columns = []
                for c in columnset:
                    columns.append(c)

                if ( 'building_lat' in columns and 'building_lon' in columns and 'stop_or_station_lat' in columns and 'stop_or_station_lon' in columns ):
                #See if row exists
                    proj_query = 'select * from wmata_dist where building_lat=\'' + srcLat + '\' and building_lon=\'' + srcLon + '\' and stop_or_station_lat=\''+ destLat + '\' and stop_or_station_lon=\'' + destLon + '\''
                    row = conn.execute(proj_query)
                    if ( row != None ):
                        conn.close()
                        engine.dispose()
                        index = columns.index("dist_in_miles")
                        return row[index]*self.meters_per_mile

                conn.close()
                engine.dispose()
            except Exception as e:
                logging.warning(e)
                logging.warning("I am unable to connect to the database")

        distReqCoords = str(srcLon) + ',' + str(srcLat) + ';' + str(destLon) + ',' + str(destLat)

        mapbox_params = self.mapbox_api_key

        # according to documentation, this doesn't work in Python SDK so switched to using REST API
        walkDistResponse = requests.get("https://api.mapbox.com/directions/v5/mapbox/walking/" + distReqCoords,params=mapbox_params)
        time.sleep(0.8)
        i = 0
        while "Too Many Requests" in str(walkDistResponse.json()) and i < 10:
            walkDistResponse = requests.get("https://api.mapbox.com/directions/v5/mapbox/walking/" + distReqCoords,params=mapbox_params)
            i = i + 1
            time.sleep(0.8)
            if i == 10:
                raise Exception('This is some exception to be defined later')
        print("Return value: " ,walkDistResponse.json()['routes'][0]['legs'][0]['distance'])
        return walkDistResponse.json()['routes'][0]['legs'][0]['distance']


    def _get_project_info(self,project,columns):
        project_info = {}
        for column_name in columns:
            if 'latitude' == column_name[0]:
                project_info['lat'] = project[columns.index(column_name)]
            elif 'longitude' == column_name[0]:
                project_info['lon'] = project[columns.index(column_name)]
            elif 'nlihc_id' == column_name[0]:
                project_info['nlihcid'] = project[columns.index(column_name)]
        return project_info

    def _find_rail_stations(self, railStations,project_details,radiusinmeters,sample=False,db='local_database'):
        """Finds all the rail stations within a given distance from a given project.  Writes to the given CSV file.

        Parameters:
        railStations - json object containing all the wmata rail station information. WMATA does not provide a 'search
                within radius' method so we have to calculate walking distance for all stops.

        project_details - dictionary containing lat, lon and nlihcid
        radiusinmeters - radius in meteres
        distCsvWriter - csvWriter for distance
        mapbox_api_key - api key for mapbox REST services
        """

        lat = project_details['lat']
        lon = project_details['lon']
        nlihc_id = project_details['nlihcid']

        for idx, station in enumerate(railStations):
            try:
                crow_distance = self._haversine(lat, lon, station['Lat'], station['Lon'])

                if crow_distance < (radiusinmeters / self.meters_per_mile):
                    walkDist = self._get_walking_distance(lat, lon, str(station['Lat']), str(station['Lon']),db=db)
                    walkDistMiles = walkDist / self.meters_per_mile
                    logging.info("crow: {}. walking: {}".format(crow_distance,walkDistMiles))
                    if walkDist <=radiusinmeters:
                        self.distOutput.append([nlihc_id, 'rail', station['Code'], "{0:.2f}".format(walkDistMiles),crow_distance, lat,lon,str(station['Lat']),str(station['Lon'])])

                else:
                    logging.info("crow: {}. {} is not close enough to calculate walking distance. ".format(crow_distance,station['Code']))
            
            except Exception as e:
                #Main error encountered was 'Null' values for project lat/lon. Returning null value
                logging.warning("Error calculating for {}".format(nlihc_id))
                self.distOutput.append([nlihc_id, 'rail', station['Code'], "Null", "Null", lat,lon,str(station['Lat']),str(station['Lon'])])

    def _haversine(self, lat1, lon1, lat2,lon2):
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
        """
        from math import radians, cos, sin, asin, sqrt

        # convert decimal degrees to radians
        original_coords = (lat1,lon1,lat2,lon2) #for debugging
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 3956 # Radius of earth in miles
        d = c * r
        #print("Haversine for {} = {}".format(original_coords,d))
        return c * r


    def _find_bus_stations(self, project_details,radiusinmeters,sample=False,db='local_database'):
        lat = project_details['lat']
        lon = project_details['lon']
        nlihc_id = project_details['nlihcid']

        wmata_headers = self._get_wmata_headers()

        params = {'Lat': lat,
                  'Lon' : lon,
                  'Radius':str(radiusinmeters)}
        response = requests.get('https://api.wmata.com/Bus.svc/json/jStops', params=params, headers=wmata_headers)
        data = response.json()

        for idx, stop in enumerate(data['Stops']):
            try:
                crow_distance = self._haversine(lat, lon, stop['Lat'], stop['Lon'])

                if crow_distance < (radiusinmeters / self.meters_per_mile):
                    walkDist = self._get_walking_distance(lat, lon, str(stop['Lat']), str(stop['Lon']),db=db)
                    walkDistMiles = walkDist / self.meters_per_mile
                    logging.info("crow: {}. walking: {}".format(crow_distance,walkDistMiles))
                    if walkDist <= radiusinmeters: #within 0.5 miles walking
                        self.distOutput.append([nlihc_id, 'bus', stop['StopID'], "{0:.2f}".format(walkDistMiles),crow_distance,lat,lon,str(stop['Lat']),str(stop['Lon'])])

                else:
                    logging.info("crow: {}. {} is not close enough to calculate walking distance. ".format(crow_distance,station['Code']))
            except Exception as e:
                #Main error encountered was 'Null' values for project lat/lon. Returning null value
                logging.warning("Error calculating for {}".format(nlihc_id))
                self.distOutput.append([nlihc_id, 'bus', stop['StopID'], "Null","Null",lat,lon,str(stop['Lat']),str(stop['Lon'])])

    def _array_to_csv(self, fields, list_of_lists, filepath):
        """
        Write the data to a csv file.

        :param fields: column headers for the data set
        :type fields: list

        :param list_of_lists: each sub-array is a single row stored as a list
        :type results: list

        :param csvfile: file path for where to write and save csv file
        :type csvfile: string

        :return: None
        """
        self.create_directory_if_missing(filepath)
        with open(filepath, 'w', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(fields)
            for row in list_of_lists:
                writer.writerow(row)
