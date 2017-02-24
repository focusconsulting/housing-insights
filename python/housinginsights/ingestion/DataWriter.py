'''
After the print(" Ready to load") statement in the main() function of load_data.py, we want to send the data stored in the newly-created clean.csv file to the database. Then, we want to update/add the appropriate row of the Postgres 'manifest' table to reflect the status of that file in the database.

Things the object will need passed to it: 
	'manifest_row',
	'meta' (memory version of meta.json)
	'csv_filename' (the path to the clean.csv file created by Cleaner)
	'overwrite' (a boolean indicating whether preexisting entries of the manifest_row['unique_data_id'] should be deleted if they exist)
'''
# import DataReader



''' 
We start with a manifest row dictionary. Each row represents a CSV. Multiple rows may correspond to one SQL table. 

1. Taking a clean csv file path from the manifest dictionary - DataSql

2. Database connection is passed through load_data.py. 

3. Check JSON meta file for how the fields should be updated in the database - insert & update vs. dropping and overwriting? - DataSql

4. Creating a SQL table if it doesn't exist - DataSql and ManifestSql 

5. Write rows - DataSql (and ManifestSql?)

share db connection
share create table if doesn't exist

DATASQL
	need to know data load type
	going to do batch update

THINK ABOUT - Has table schema changed? Column names, number of columns, column data types

	if we have ten rows and five already exist, does database know how to update or is that on us?



are we overriding or appending? 
	if overriding - prep and write
	if update - need to define unique key for each row in each table - maybe something for DataReader class? JSON file?



'''

import os

class HISql(object):
	# def __init__(self, root):
	# 	# get filepath of file
	# 	self._root = os.getcwd()
	# 	# self.filename = filename

	# 	# create table if exists

	# def returnRoot():
	# 	return 

class DataSql(HISql):
	def __init__(self, db_conn, manifest_dict, meta_field):
		self.db_conn = db_conn
		self.manifest_dict = manifest_dict
		self.meta_field = meta_field

	# def read_manifest(self):

	def read_and_write_to_sql(self):
		# include flag check done in datareader should_file_be_loaded
		# need table name, local folder , file path, unique data id

		# Get manifest info
		self.tablename = self.manifest_dict["destination_table"]
		self.path = os.path.join(self.manifest_dict["local_folder"], self.manifest_dict["filepath"])
		self.unique_data_id = self.manifest_dict["unique_data_id"]

		self.tablename
		# check to see if table exists in database - look up how to iterate through sqlalchemy database when connected - stackoverflow

			# if table doesn't exist, create the table: 
				# open json file
				# for each field, create a column with the appropriate type, use the correct sql_name for the header - look up best way to do this. 

		# read json and determine how to update database table if necessary. we need to look at specific example for this. way to update rows based on existing criteria?

		# if not done, batch update all rows using COPY FROM postgres command. As far as we know, COPY FROM appends new rows to the table. What's the best way to selectively insert and update? Dropping all old rows using unique key?





thing = HISql()
print(thing.returnRoot())
# class ManifestSql(HISql):
# 	def __init__(self, path):

# 	def get_row(self, unique_data_id):  



