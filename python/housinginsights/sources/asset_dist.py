import os
import json
import requests
import time
import csv
from housinginsights.tools.logger import HILogger
from housinginsights.sources.base import BaseApiConn
import housinginsights.tools.dbtools as dbtools


logger = HILogger(name=__file__, logfile="sources.log")


class AssetApiConn(BaseApiConn):
    def __init__(self,
                 baseurl=None,
                 proxies=None,
                 database_choice=None,
                 debug=False,
                 use_cached_distance=False
                 ):
        baseurl = None
        super().__init__(baseurl, proxies=proxies, debug=debug)
        self.meters_per_mile = 1609.344
        self.use_cached_distance = use_cached_distance
        # pull API keys
        secretsFileName = os.path.abspath(
            os.path.join(os.path.dirname(__file__),
                         os.pardir, "secrets.json")
                        )
        self.api_keys = json.loads(open(secretsFileName).read())
        self.wmata_api_key = self.api_keys['wmata']['api_key']
        self.mapbox_api_key = {
            'access_token':
            self.api_keys['mapbox']['public-token']}

        self._available_unique_data_ids = ["asset_dist"]

    def getCharterSchoolData(self, conn):
        school_query = 'select * from charter_schools'
        rows = conn.execute(school_query)
        return rows.fetchall()

    def _get_meters(self, miles):
        self.miles = miles
        self.meters = miles*self.meters_per_mile
        return self.meters

    def _get_project_info(self, project, columns):
        project_info = {}
        for column_name in columns:
            if 'latitude' == column_name[0]:
                project_info['lat'] = project[columns.index(column_name)]
            elif 'longitude' == column_name[0]:
                project_info['lon'] = project[columns.index(column_name)]
            elif 'nlihc_id' == column_name[0]:
                project_info['nlihcid'] = project[columns.index(column_name)]
        return project_info

    def _haversine(self, lat1, lon1, lat2, lon2):
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
        """
        from math import radians, cos, sin, asin, sqrt

        # convert decimal degrees to radians
        # original_coords = (lat1, lon1, lat2, lon2) # for debugging
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 3956  # Radius of earth in miles
        # print("Haversine for {} = {}".format(original_coords,d))
        return c * r

    def _get_walking_distance(
        self,
        srcLat,
        srcLon,
        destLat,
        destLon,
        db='local_database'
    ):
        """Returns the walking distance in meters between two locations

        Parameters:
        srcLat - latitude for source location
        srcLon - longitude for source location
        destLat - latitude for destination location
        destLon - longitude for destination location
        mapbox_api_key - api key for mapbox REST services
        """

        if self.use_cached_distance is True:
            try:
                # Configure the connection
                engine = dbtools.get_database_engine(db)
                conn = dbtools.get_database_connection(db)

                # Pull columns to see if the database has updated columns in wmata_dist
                columnset = conn.execute('select column_name from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME=\'asset_dist\'')
                columns = []
                for c in columnset:
                    columns.append(c[0])

                if (
                    'building_lat' in columns and
                    'building_lon' in columns and
                    'stop_or_station_lat' in columns and
                    'stop_or_station_lon' in columns
                    ):
                    # See if row exists
                    proj_query = 'select * from wmata_dist where building_lat=\'' + str(srcLat) + '\' and building_lon=\'' + str(srcLon) + '\' and stop_or_station_lat=\''+ str(destLat) + '\' and stop_or_station_lon=\'' + str(destLon) + '\''
                    proxy = conn.execute(proj_query)
                    results = [dict(x) for x in proxy.fetchall()]

                    if (len(results) != 0):
                        logger.info("  Found cached row!")
                        walking_distance = results[0]['dist_in_miles']

                        conn.close()
                        engine.dispose()

                        return float(walking_distance)*self.meters_per_mile
                    else:
                        logger.info("  Couldn't find cached row for %s", proj_query)
                else:
                    logger.info("Couldn't find all columns")

                conn.close()
                engine.dispose()
            except Exception as e:
                logger.error("Unable to connect to the database: %s", e)

        distReqCoords = str(srcLon) + ',' + str(srcLat) + ';' + str(destLon) + ',' + str(destLat)

        mapbox_params = 'access_token=pk.eyJ1IjoiY29kZWZvcmRjIiwiYSI6ImNrOGxuanFxcTBiY3ozbGwzMXcyNHFzcHYifQ.mm8SMJASaeYdkbI12WUqhw'
        # according to documentation, this doesn't work in Python SDK
        walkDistResponse = requests.get("https://api.mapbox.com/directions/v5/mapbox/walking/" + distReqCoords, params=mapbox_params)
        time.sleep(0.8)
        i = 0
        while "Too Many Requests" in str(walkDistResponse.json()) and i < 10:
            walkDistResponse = requests.get("https://api.mapbox.com/directions/v5/mapbox/walking/" + distReqCoords, params=mapbox_params)
            i = i + 1
            time.sleep(0.8)
            if i == 10:
                raise Exception('This is some exception to be defined later')
        logger.debug("Return value: ", walkDistResponse.json()['routes'][0]['legs'][0]['distance'])
        return walkDistResponse.json()['routes'][0]['legs'][0]['distance']

    def _find_all_assets(self, assets, radius, project, db='local_database'):
        lat = project['lat']
        lon = project['lon']
        nlihc_id = project['nlihcid']
        for idx, asset in enumerate(assets):
            try:
                crow_distance = self._haversine(lat, lon, asset['latitude'], asset['longitude'])
                (radius / self.meters_per_mile)
                if crow_distance < (radius / self.meters_per_mile):
                    logger.info('Getting walking distance for {} - {}'.format(nlihc_id, asset['name']))
                    walkDist = self._get_walking_distance(lat, lon, str(asset['latitude']), str(asset['longitude']), db=db)
                    walkDistMiles = walkDist / self.meters_per_mile
                    logger.info("crow: %s. walking: %s", crow_distance, walkDistMiles)
                    logger.info('Calculated %s distance for  %s - %s', walkDistMiles, nlihc_id, asset['name'])
                    if walkDist <= radius:
                        self.distOutput.append([
                            nlihc_id,
                            'education',
                            asset['school_id'],
                            asset['name'],
                            "{0:.2f}".format(walkDistMiles),
                            crow_distance,
                            lat,
                            lon,
                            str(asset['latitude']),
                            str(asset['longitude'])])
            except Exception as e:
                logger.error('Error calculating for %s %s', nlihc_id, e)
                self.distOutput.append([
                            nlihc_id,
                            'education',
                            asset['school_id'],
                            asset['name'],
                            'Null',
                            'Null',
                            lat,
                            lon,
                            str(asset['latitude']),
                            str(asset['longitude'])])

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
    
    def get_data(
        self,
        unique_data_ids=None,
        sample=False,
        output_type='csv',
        db='local_database', **kwargs
    ):
        self.distOutput = []
        self.distHeader = (
            'nlihc_id',
            'type',
            'id',
            'asset_name',
            'dist_in_miles',
            'crow_distance',
            'building_lat',
            'building_lon',
            'asset_lat',
            'asset_lon'
        )
        logger.info("Beginning to fetch distances for assets")
        try:
            engine = dbtools.get_database_engine(db)
            conn = dbtools.get_database_connection(db)
            logger.info("  Connected to Housing Insights database")
            columnset = conn.execute('select column_name from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME=\'project\'')

            # Get all the project
            projects_query = 'select * from project'
            rows = conn.execute(projects_query)
        except Exception as e:
            conn.close()
            engine.dispose()
            logger.error("Could not fetch project rows: %s", e)

        columns = []
        for c in columnset:
            columns.append(c)
        # numrow = 0
        # total_rows = rows.rowcount

        try:
            charter_schools = self.getCharterSchoolData(conn)
        except Exception as e:
            logger.error("Could not fetch asset data %s", e)
            conn.close()
            engine.dispose

        logger.info('About to process {} projects and {} assets'.format(rows.rowcount, len(charter_schools)))
        for idx, row in enumerate(rows):
            radius = self._get_meters(0.5)
            project_details = self._get_project_info(row, columns)
            lat = project_details['lat']
            lon = project_details['lon']
            
            if lat is None or lon is None:
                logger.warning('Latitude or Longitude not availabe for project {}'.format(project_details['nlihcid']))
                continue
            self._find_all_assets(charter_schools, radius, project_details)
        logger.info("Done getting distance")
        self._array_to_csv(self.distHeader, self.distOutput, self.output_paths['asset_dist'])
            
