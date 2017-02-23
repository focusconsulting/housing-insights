# Helps create a path to the tools directory.
if __name__ == '__main__':
  import sys, os
  sys.path.append(os.path.abspath("../../"))

import requests
import time
import csv

urls = []

# Connect to database.
def get_db_squares():
	from housinginsights.tools import database

	# Use appropriate database name from secrets.json. 
	database_connection = database.get_database_connection("remote_database")
	# Selects property squares from DC tax data. Returns list of tuples.
	query_result = database_connection.execute("SELECT DISTINCT substring(ssl FROM 1 for 4) FROM dc_tax;")
	# For every tuple in the list.
	for row in query_result:
		# For each value in the tuple, push to the urls list.
		for value in row:
			urls.append("https://maps2.dcgis.dc.gov/dcgis/rest/services/DCOZ/Zone_Mapservice/MapServer/25/query?f=json&where=Square =" + "'" + value + "'" + "&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*")
			print(value)
	database_connection.close()
	return urls

def write_values():
	all_urls = get_db_squares()
	all_zoning_data = fetch_zoning_data(all_urls) 

	# Headers
	fieldnames = (['ANCSMD', 'Action_Taken', 'ApprovedZoning', 'CasePoint_Number', 'CasePoint_URL', 'Case_ID', 'Case_Name', 'Case_Type', 'Description', 'LotNum', 'OBJECTID', 'OwnerName', 'Parcel', 'Premise_Address', 'SSL', 'Square', 'Suffix', 'URL', 'case_number', 'case_type_relief', 'dateFiled', 'existingZoning', 'relatedCases', 'reliefSought', 'requestedZoning'])

	for filename, filelist in all_zoning_data.items():
		with open(filename + ".csv", "w") as zoningcsv:
			writer = csv.DictWriter(zoningcsv, fieldnames=fieldnames)
			writer.writeheader()
			for line in filelist:
				writer.writerow(line)

def fetch_zoning_data(urls):
	# Creates two lists for zoning data. List names are used as CSV filenames.  
	zoning_data = {
			"empty_zoning_data": [], 
			"existing_zoning_data": []
		}

	for url in urls: 
		r = requests.get(url)
		if (r.status_code >= 200 and r.status_code < 400):
			response = r.json()
			zoning_key = response["features"]
			
			for data in zoning_key:
				datakey = data["attributes"]
				if (not datakey["case_type_relief"]):
					zoning_data["empty_zoning_data"].append(datakey)
				else:
					zoning_data["existing_zoning_data"].append(datakey)
				print(data)
		
		else: 
			print ("ERROR - Status code: " + str(r.status_code))
		# Pause for three secs so we don't overload server.
		time.sleep(3)
	return zoning_data

if __name__ == '__main__':
	write_values()
