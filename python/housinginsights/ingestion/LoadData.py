"""
Modulel loads our flat file data into the Postgres database. It will rebuild the
database of choice with sample or real data by first deleting any data in the
repository, and then re-load the data into the repository.

If you want to rebuild the data with actual data (i.e. what is in manifest.csv
instead of manifest.csv), run the same command without ‘sample’ at the end.

Notes:
 - manifest.csv has every flat file that needs to be loaded (i.e. CSV's we have
 downloaded).
 - other scripts can get data that is available from APIs, so manifest won't
 reflect all the data we are including.
 - meta.json provides meta information about our *SQL* tables. Note that
 because multiple CSV's can go into the same table (i.e. two different versions
 of the same data), there will be more rows in the CSV than there are 'tables'
 in the json.
"""

import sys
import os
import logging
import argparse
import json

from sqlalchemy import Table, Column, Integer, String, MetaData, Numeric
from datetime import datetime
import dateutil.parser as dateparser

# Needed to make relative package imports when running this file as a script
# (i.e. for testing purposes).
# Read why here: https://www.blog.pythonlibrary.org/2016/03/01/python-101-all
# -about-imports/

PYTHON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           os.pardir, os.pardir))

logging_path = os.path.abspath(os.path.join(PYTHON_PATH, "logs"))
logging_filename = os.path.abspath(os.path.join(logging_path, "ingestion.log"))

#append to path if running this file directly, otherwise assume it's already been appended. 
if __name__ == "__main__":
    sys.path.append(PYTHON_PATH)

from housinginsights.tools import dbtools

from housinginsights.ingestion import CSVWriter, DataReader
from housinginsights.ingestion import HISql, TableWritingError
from housinginsights.ingestion import functions as ingestionfunctions
from housinginsights.ingestion.Manifest import Manifest


class LoadData(object):

    def __init__(self, database_choice=None, meta_path=None,
                 manifest_path=None, keep_temp_files=True, drop_tables=False):
        """
        Initializes the class with optional arguments. The default behaviour 
        is to load the local database with data tracked from meta.json 
        and manifest.csv within the 'python/scripts' folder.
        
        :param database_choice: choice of 'local_database', 
        'docker_database', and 'remote_database'
        :param meta_path: the path of the meta.json to be used
        :param manifest_path: the path of the manifest_path.csv to be used
        :param keep_temp_files: if True, temp clean pipe-delimited files will be
        archived in the 'python/logs' folder
        """

        # load defaults if no arguments passed
        _scripts_path = os.path.abspath(os.path.join(PYTHON_PATH, 'scripts'))
        if database_choice is None:
            self.database_choice = 'docker_database'
        else:
            self.database_choice = database_choice
        if meta_path is None:
            meta_path = os.path.abspath(os.path.join(_scripts_path,
                                                     'meta.json'))
        if manifest_path is None:
            manifest_path = os.path.abspath(os.path.join(_scripts_path,
                                                         'manifest.csv'))
        self._keep_temp_files = keep_temp_files

        # load given meta.json and manifest.csv files into memory
        self.meta = ingestionfunctions.load_meta_data(meta_path)
        self.manifest = Manifest(manifest_path)

        # setup engine for database_choice
        self.engine = dbtools.get_database_engine(self.database_choice)

        # write the meta.json to the database
        self._meta_json_to_database()

        self._failed_table_count = 0

        self.drop_tables = drop_tables

    def _drop_tables(self):
        """
        Returns the outcome of dropping all the tables from the 
        database_choice and then rebuilding.
        """
        logging.info("Dropping all tables from the database!")
        db_conn = self.engine.connect()
        query_result = list()
        query_result.append(db_conn.execute(
            "DROP SCHEMA public CASCADE;CREATE SCHEMA public;"))

        if self.database_choice == 'remote_database' or self.database_choice \
                == 'remote_database_master':
            query_result.append(db_conn.execute('''
            GRANT ALL PRIVILEGES ON SCHEMA public TO housingcrud;
            GRANT ALL PRIVILEGES ON ALL TABLES    IN SCHEMA public TO housingcrud;
            GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO housingcrud;
            GRANT ALL ON SCHEMA public TO public;
            '''))
        return query_result

    def _meta_json_to_database(self):
        """
        Makes sure we have a meta table in the database.
        If not, it creates it with appropriate fields.
        """

        sqlalchemy_metadata = MetaData()  # this is unrelated to our meta.json
        meta_table = Table('meta', sqlalchemy_metadata,
                           Column('meta', String))

        sqlalchemy_metadata.create_all(self.engine)
        json_string = json.dumps(self.meta)
        ins = meta_table.insert().values(meta=json_string)
        conn = self.engine.connect()
        conn.execute("DELETE FROM meta;")
        conn.execute(ins)

    def _remove_existing_data(self, uid, manifest_row):
        """
        Removes all rows in the respective table for the given unique_data_id
        then sets status = deleted for the unique_data_id in the
        database manifest.

        :param uid: unique_data_id for the data to be updated
        :param manifest_row: the row for uid in the manifest
        :return: result from executing delete query as
        sqlalchemy result object if row exists in sql manifest - else
        returns None
        """
        temp_filepath = self._get_temp_filepath(
            manifest_row=manifest_row)

        # get objects for interfacing with the database
        sql_interface = self._configure_db_interface(
            manifest_row=manifest_row, temp_filepath=temp_filepath)
        sql_manifest_row = sql_interface.get_sql_manifest_row()

        try:
            # delete only rows with data_id in respective table
            table_name = sql_manifest_row['destination_table']
            query = "DELETE FROM {} WHERE unique_data_id =" \
                    " '{}'".format(table_name, uid)
            logging.info("\t\tDeleting {} data from {}!".format(
                uid, table_name))
            result = self.engine.execute(query)

            # change status = deleted in sql_manifest
            logging.info("\t\tResetting status in sql manifest row!")
            sql_interface.update_manifest_row(conn=self.engine,
                                              status='deleted')

            return result
        except TypeError:
            logging.info("\t\tNo sql_manifest exists! Proceed with adding"
                         " new data to the database!")

        return None

    def _get_most_recent_timestamp_subfolder(self, root_folder_path):
        """
        Returns the most recent timestamp subfolder in a given folder path.

        :param root_folder_path: the path for the directory containing
        timestamp subfolders
        :type root_folder_path: str

        :return: most recent timestamp subfolder
        :type: str
        """
        walk_gen = os.walk(root_folder_path)
        root, dirs, files = walk_gen.__next__()
        dirs.sort(reverse=True)
        return dirs[0]

    def make_manifest(self, all_folders_path):
        """
        Creates a new manifest.csv with updated data date and filepath for
        the raw data files within the most recent timestamp subfolder of the
        given folder path.

        A new instance of manifest object is created from the new
        manifest.csv file.

        :param all_folders_path: the folder that contains the timestamped
        subfolders representing updated raw data files that should be loaded
        into the database
        :type all_folders_path: str

        :param overwrite: should the current manifest.csv be overwritten?
        :type overwrite: bool

        :return: the path of the manifest
        """
        # get most recent subfolder, gather info for updating manifest
        timestamp = self._get_most_recent_timestamp_subfolder(
            all_folders_path)
        most_recent_subfolder_path = os.path.join(all_folders_path,
                                                  timestamp)

        return self.manifest.update_manifest(most_recent_subfolder_path)

    def update_database(self, unique_data_id_list):
        """
        Reloads only the flat file associated to the unique_data_id in
        unique_data_id_list.

        Returns a list of unique_data_ids that were successfully updated.
        """
        logging.info("update_only(): attempting to update {} data".format(
            unique_data_id_list))
        processed_data_ids = []

        for uid in unique_data_id_list:
            manifest_row = self.manifest.get_manifest_row(uid)

            # process manifest row for requested data_id if flagged for use
            if manifest_row is None:
                logging.info("\tSkipping: {} not found in manifest!".format(
                    uid))
            else:
                logging.info("\tManifest row found for {} - preparing to "
                             "remove data.".format(uid))
                self._remove_existing_data(uid=uid, manifest_row=manifest_row)

                # follow normal workflow and load data_id
                logging.info(
                    "\tLoading {} data!".format(uid))
                self._process_data_file(manifest_row=manifest_row)
                processed_data_ids.append(uid)

        # build Zone Facts table
        self._create_zone_facts_table()

        return processed_data_ids

    def _get_temp_filepath(self, manifest_row):
        """
        Returns a file path where intermediary clean psv file will be saved.
        """
        return os.path.abspath(
                    os.path.join(logging_path, 'temp_{}.psv'.format(
                        manifest_row['unique_data_id'])))

    def rebuild(self):
        """
        Using manifest.csv, meta.json, and respective cleaners, validate and
        process the data and then load all usable data into the database
        after dropping all tables.
        """
        if self.drop_tables:
            self._drop_tables()

        # reload meta.json into db
        self._meta_json_to_database()

        processed_data_ids = []

        # Iterate through each row in the manifest then clean and validate
        for manifest_row in self.manifest:
            # Note: Incompletely filled out rows in the manifest can break the
            # other code
            # TODO: figure out a way to flag this issue early in loading
            # TODO: of manifest

            # only clean and validate data files flagged for use in database
            if manifest_row['include_flag'] == 'use':
                logging.info("{}: preparing to load row {} from the manifest".
                             format(manifest_row['unique_data_id'],
                                    len(self.manifest)))

                self._process_data_file(manifest_row=manifest_row)

            processed_data_ids.append(manifest_row['unique_data_id'])

        # build Zone Facts table
        self._create_zone_facts_table()

        return processed_data_ids

    def _create_zone_facts_table(self):
        """
        Creates the zone_facts table which is used as a master table for API
        endpoints. The purpose is to avoid recalculating fields adhoc and
        performing client-side reconfiguration of data into display fields.
        This is all now done in the backend whenever new data is loaded.

        :return: a immutable dict that contains the tables structure of the
        table and sqlAlchemy metadata object used.
        """
        # drop zone_facts table if already in db
        if 'zone_facts' in self.engine.table_names():
            with self.engine.connect() as conn:
                conn.execute('DROP TABLE zone_facts;')

        # create empty zone_facts table
        metadata = MetaData(bind=self.engine)
        zone_facts = Table('zone_facts', metadata,
                           Column('zone_type', String),
                           Column('zone', String, primary_key=True),
                           Column('poverty_rate', Numeric),
                           Column('fraction_black', Numeric),
                           Column('income_per_capita', Numeric),
                           Column('labor_participation', Numeric),
                           Column('fraction_foreign', Numeric),
                           Column('fraction_single_mothers', Numeric),
                           Column('acs_lower_rent_quartile', Numeric),
                           Column('acs_median_rent', Numeric),
                           Column('acs_upper_rent_quartile', Numeric),
                           Column('crime_count', Numeric),
                           Column('violent_crime_count', Numeric),
                           Column('non_violent_crime_count', Numeric),
                           Column('crime_rate', Numeric),
                           Column('violent_crime_rate', Numeric),
                           Column('non_violent_crime_rate', Numeric),
                           Column('building_permits', Numeric),
                           Column('construction_permits', Numeric))

        # add to db
        metadata.create_all(tables=[zone_facts])

        # populate table with calculated fields values
        self._populate_zone_facts_table()

        return metadata.tables

    def _populate_zone_facts_table(self):
        """
        Populates the zone_facts table with the calculated fields data and
        acs rent data fields from census.

        :return: list of SQLAlchemy query result objects from inserting the
        calculated fields data into the zone_facts table.
        """
        # list of zone_fact headers created from census table
        census_fields = [
            'poverty_rate', 'fraction_black', 'income_per_capita',
            'labor_participation', 'fraction_foreign',
            'fraction_single_mothers', 'acs_lower_rent_quartile',
            'acs_median_rent', 'acs_upper_rent_quartile'
        ]

        # dict with key/list pairs for calling summarize_observations method
        summarize_obs_field_args = {  # [method, table_name, filter_name]
            'crime_count': ['count', 'crime', 'all'],
            'violent_crime_count': ['count', 'crime', 'violent'],
            'non_violent_crime_count': ['count', 'crime', 'nonviolent'],
            'crime_rate': ['rate', 'crime', 'all'],
            'violent_crime_rate': ['rate', 'crime', 'violent'],
            'non_violent_crime_rate': ['rate', 'crime', 'nonviolent'],
            'building_permits': ['count', 'building_permits', 'all'],
            'construction_permits': ['count', 'building_permits',
                                     'construction']
        }

        zone_types = ['census_tract', 'ward', 'neighborhood_cluster']

        query_results = list()

        # populate columns accordingly for each zone_specific type
        for zone_type in zone_types:
            field_values = dict()

            # get field value from census table
            for field in census_fields:
                result = self._census_with_weighting(data_id=field,
                                                     grouping=zone_type)
                field_values[field] = result['items']

            # get field value from building permits and crime table
            for field in summarize_obs_field_args:
                method, table_name, filter_name = summarize_obs_field_args[
                    field]
                result = self._summarize_observations(method, table_name,
                                                      filter_name,
                                                      months=12,
                                                      grouping=zone_type)
                field_values[field] = result['items']

            zone_specifics = self._get_zone_specifics_for_zone_type(zone_type)

            # TODO: add aggregate for each zone_type into table
            for zone in zone_specifics:
                # skip 'Non-cluster area'
                if zone == 'Non-cluster area':
                    continue

                # get not None values so we can added to db
                columns = list()
                values = list()

                for field in field_values:
                    field_val = field_values[field]

                    # only proc
                    if field_val is not None and zone in field_val:
                        zone_value = field_val[zone]

                        if zone_value is not None:
                            columns.append(field)
                            values.append("'" + str(zone_value) + "'")

                # derive column and values strings needed for sql query
                columns = ', '.join(columns)
                columns = 'zone_type, zone, ' + columns

                values = ', '.join(values)
                values = "'" + zone_type + "', '" + zone + "', " + values

                q = "INSERT INTO zone_facts ({cols}) VALUES ({vals})".format(
                    cols=columns, vals=values)

                with self.engine.connect() as conn:
                    result = conn.execute(q)
                    query_results.append(result)

        return query_results

    def _get_zone_specifics_for_zone_type(self, zone_type):
        """
        Returns a list of zone_specific values for a given zone_type.
        """
        with self.engine.connect() as conn:

            if zone_type == 'ward':
                table = 'census_tract_to_ward'
            elif zone_type == 'neighborhood_cluster':
                table = 'census_tract_to_neighborhood_cluster'
            else:
                table = 'census'

            query_result = conn.execute(
                'select distinct {zone} from {table};'.format(zone=zone_type,
                                                              table=table))
            zone_specifics = [row[0] for row in query_result.fetchall()]
            # zones.append(zone)

        return zone_specifics

    def _items_divide(self, numerator_data, denominator_data):
        """
        Divides items in the numerator by items in the denominator by matching
        the appropriate groupings.

        Takes data that is formatted for output the API, i.e. a dictionary
        with key "items", which contains a list of dictionaries each with 'grouping'
        and 'count'.

        Returns items as dictionary with group and division result as
        key/value pairs instead of list of dictionaries.
        """
        items = dict()
        if numerator_data['items'] is None:
            items = None
        else:
            for n in numerator_data['items']:
                # TODO what should we do when a matching item isn't found?

                if n not in denominator_data['items'] or \
                                numerator_data['items'][n] is None \
                        or denominator_data['items'][n] is None:
                    divided = None
                else:
                    divided = numerator_data['items'][n] / denominator_data[
                        'items'][n]

                # item = dict({'group': n['group'],
                #              'value': divided})
                items[n] = divided

        return {'items': items, 'grouping': numerator_data['grouping'],
                'data_id': numerator_data['data_id']}

    def _census_with_weighting(self, data_id, grouping):
        """
        Zone facts table helper function to get data from our census table.\

        :param data_id: must either be a column name or a custom calculated
        value.

        :param grouping: either 'census_tract', 'ward',
        or 'neighborhood_cluster'.

        :return: dictionary with 'items', 'grouping', and 'data_id' as keys.
        Items stores the results for the calculated data_id for the grouping.
        """

        calculated_values = {
            'poverty_rate': 'population_poverty',
            'fraction_black': 'population_black',
            'income_per_capita': 'aggregate_income',
            'labor_participation': 'population_working',
            'fraction_foreign': 'population_foreign',
            'fraction_single_mothers': 'population_single_mother'
        }

        if data_id in calculated_values:

            field = calculated_values[data_id]
            numerator = self._get_weighted_census_results(grouping, field)
            denominator = self._get_weighted_census_results(grouping,
                                                            'population')

            api_results = self._items_divide(numerator, denominator)
            api_results['data_id'] = data_id

        # If data_id isn't one of our custom ones, assume it is a column name
        else:
            api_results = self._get_weighted_census_results(grouping, data_id,
                                                            pop_wt_prop=True)

        return api_results

    def _get_weighted_census_results(self, grouping, field, pop_wt_prop=False):
        """
        Queries the census table for the relevant field and returns the results
        as a weighted count returns the standard 'items' format.

        Currently only implemented for the 'counts' weighting factor not for
        the proportion version.

        :param pop_wt_prop: determine which weighting factor to use. 'False'
        implies should use population_weight_counts - use for anything that is
        a total sum for the zone (i.e. total income, total people working, etc.)

        'True' implies should use population_weight_proportion - used for
        weighting proportion, mean, and median. Note - not quite statistically
        accurate and should be only used when the source data size is not
        useful.
        """
        # configure weighting factor to be used
        pop_wt = 'population_weight_counts'
        if pop_wt_prop:
            pop_wt = 'population_weight_proportions'

        with self.engine.connect() as conn:
            q = "SELECT census_tract, {field} FROM census".format(
                field=field)  # TODO need to add 'year' column for multiple census years when this is added to the data
            proxy = conn.execute(q)
            census_results = [dict(x) for x in proxy.fetchall()]

            # Transform the results
            items = dict()  # For storing results as we go

            if grouping == 'census_tract':
                # No weighting required, data already in proper format
                for r in census_results:
                    items[r['census_tract']] = r[field]

            elif grouping in ['ward', 'neighborhood_cluster']:
                proxy = conn.execute(
                    "SELECT DISTINCT {grouping} FROM census_tract_to_{grouping}".format(
                        grouping=grouping))
                groups = [x[0] for x in proxy.fetchall()]

                for group in groups:
                    proxy = conn.execute(
                        "SELECT * FROM census_tract_to_{grouping} WHERE {grouping} = '{group}'".format(
                            grouping=grouping, group=group))
                    results = [dict(x) for x in proxy.fetchall()]

                    count = 0
                    for result in results:
                        tract = result['census_tract']
                        factor = result[pop_wt]
                        matching_data = next((item for item in census_results if
                                              item["census_tract"] == tract),
                                             {field: None})
                        if matching_data[field] is None:
                            logging.warning(
                                "Missing data for census tract when calculating weightings: {}".format(
                                    tract))
                            matching_data[field] = 0

                        value = matching_data[field]
                        count += (value * factor)

                    # output = dict({'group': group, 'value': round(count, 0)})
                    # items.append(output)
                    items[group] = round(count, 0)
            else:
                # Invalid grouping
                items = None

        return {'items': items, 'grouping': grouping, 'data_id': field}

    def _summarize_observations(self, method, table_name, filter_name, months,
                                grouping):
        """
        This endpoint takes a table that has each record as list of observations
        (like our crime and building_permits tables) and returns summary
        statistics either as raw counts or as a rate, optionally filtered.

        :param method: "count" or "rate"
        :param table_name: name of the table in the database, e.g.
        'building_permits' or 'crime'
        :param filter_name: code name of the filter to apply to the data, which
        varies by table
                    "all" - no filtering applied
                    "construction" - only building_permits with permit_type_name
                        = 'CONSTRUCTION'
                    "violent" - only crimes where the offense type is a violent
                        crime (note, not 100% match, need to compare DCPD definitions to official to verify)
                    "nonviolent" - the other crime incidents
        :param months: The number of months of date to include. By default this
        is from now() but can be modified by an optional parameter
        :param grouping: What to use for the 'GROUP BY' clause, e.g. 'ward',
        'neighbourhood_cluster', 'zip', 'census_tract'.

        Can accept any valid column name, so 'offense' for crime or
        'permit_type_name' for building_permits are also valid

        Optional params:
        start: YYYYMMDD format start date to use instead of now() for the duration filter


        replaces the count_all method that is deprecated

        Example working URLS:
        /api/count/crime/all/12/ward - count of all crime incidents
        /api/count/building_permits/construction/12/neighborhood_cluster - all
        construction permits in the past year grouped by neighborhood_cluster

        :return:
        """


        ###########################
        #Handle filters
        ###########################
        #Be sure concatenated 'AND' statements have a space in front of them
        additional_wheres = ''
        if filter_name == 'all':
            additional_wheres += " "

        # Filter options for building_permits
        elif filter_name == 'construction':
            additional_wheres += " AND permit_type_name = 'CONSTRUCTION' "

        # Filter options for crime
        elif filter_name == 'violent':
            additional_wheres += " AND OFFENSE IN ('ROBBERY','HOMICIDE','ASSAULT W/DANGEROUS WEAPON','SEX ABUSE')"
        elif filter_name == 'nonviolent':
            additional_wheres += " AND OFFENSE NOT IN ('ROBBERY','HOMICIDE','ASSAULT W/DANGEROUS WEAPON','SEX ABUSE')"


        # Fallback for an invalid filter
        else:
            additional_wheres += " Incorrect filter name - this inserted SQL will cause query to fail"

        ##########################
        #Handle date range
        ##########################
        date_fields = {'building_permits': 'issue_date',
                       'crime': 'report_date'}
        date_field = date_fields[table_name]

        #method currently not implemented. 'count' or 'rate'

        start_date = None #request.args.get('start')
        print("Start_date found: {}".format(start_date))
        if start_date is None:
            start_date = "now()"
        else:
            start_date = dateparser.parse(start_date, dayfirst=False,
                                          yearfirst=False)
            start_date = datetime.strftime(start_date, '%Y-%m-%d')
            start_date = "'" + start_date + "'"

        date_range_sql = (
            "({start_date}::TIMESTAMP - INTERVAL '{months} months')"
            " AND {start_date}::TIMESTAMP"
            ).format(start_date=start_date, months=months)

        #########################
        # Optional - validate other inputs
        #########################
        # Should we restrict the group by to a specific list, or allow whatever
        # people want?
        # Ditto for table name

        ###############
        # Get results
        ###############
        api_results = self._count_observations(table_name, grouping, date_field,
                                               date_range_sql,
                                               additional_wheres)

        # Edit the data_id. TODO this is not specific enough, need univeral system for handling unique data ids to be used on front end.
        # Is this better handled here in the API or front end exclusively?
        api_results['data_id'] += '_' + filter_name

        # Apply the normalization if needed
        if method == 'rate':
            # TODO: need to complete get_residential_permits method
            if table_name in ['building_permits']:
                denominator = self._get_residential_units(grouping)
                api_results = self._items_divide(api_results, denominator)
                api_results = self._scale(api_results, 1000)  # per 1000
                # residential units
            if table_name in ['crime']:
                denominator = self._get_weighted_census_results(grouping,
                                                           'population')
                api_results = self._items_divide(api_results, denominator)
                api_results = self._scale(api_results,
                                          100000)  # crime incidents per 100,000 people

        # Output as JSON
        return api_results

    def _count_observations(self, table_name, grouping, date_field,
                            date_range_sql, additional_wheres=''):
        fallback = "'Unknown'"

        try:
            with self.engine.connect() as conn:
                override_group = False  # flag tracking if group is overridden

                # prepare to handle census_tract not in building_permits table
                if table_name == 'building_permits' and grouping == \
                        'census_tract':
                    override_group = True
                    grouping = 'ward'

                q = """
                    SELECT COALESCE({grouping},{fallback}) --'Unknown'
                    ,count(*) AS records
                    FROM {table_name}
                    where {date_field} between {date_range_sql}
                    {additional_wheres}
                    GROUP BY {grouping}
                    ORDER BY {grouping}
                    """.format(grouping=grouping, fallback=fallback,
                               table_name=table_name, date_field=date_field,
                               date_range_sql=date_range_sql,
                               additional_wheres=additional_wheres)

                proxy = conn.execute(q)
                results = proxy.fetchall()

                #transform the results.
                #TODO should come up with a better generic way to do this using column
                  #names for any arbitrary sql table results.
                formatted = dict()  # TODO: use dict comprehension
                for x in results:
                    # dictionary = dict({'group': x[0], 'value': x[1]})
                    formatted[x[0]] = x[1]

                # handle census_tract not in building_permit table scenario
                if override_group:
                    # get census_tract to ward count factor
                    q = """
                        SELECT census_tract, ward, population_weight_counts
                        FROM census_tract_to_ward
                        """
                    proxy = conn.execute(q)
                    results = proxy.fetchall()

                    # use factoring to get census_tract related counts
                    items = dict()

                    for row in results:
                        tract, ward, factor = row
                        count = items.get(tract, 0)
                        items[tract] = count + formatted[ward] * factor

                    formatted = items

            return {'items': formatted, 'grouping': grouping,
                    'data_id': table_name}

        #TODO do better error handling - for interim development purposes only
        except Exception as e:
            return {'items': None, 'notes': "Query failed: {}".format(e),
                    'grouping': grouping, 'data_id': table_name}

    def _scale(self, data, factor):
        """
        Multiplies each of the items 'count' entry by the factor
        """

        for zone in data['items']:
            try:
                data['items'][zone] *= factor
            except Exception as e:
                data['items'][zone] = None

        return data

    def _get_residential_units(self, grouping):
        """
        Returns the number of residential units in the standard 'items' format
        """
        # TODO implement me
        return None

    def _process_data_file(self, manifest_row):
        """
        Processes the data file for the given manifest row.
        """
        # get the file object for the data
        csv_reader = DataReader(meta=self.meta,
                                manifest_row=manifest_row,
                                load_from="file")

        # get file path for storing clean PSV files
        temp_filepath = self._get_temp_filepath(manifest_row=manifest_row)

        # validate and clean
        self._load_single_file(table_name=manifest_row['destination_table'],
                               manifest_row=manifest_row,
                               csv_reader=csv_reader,
                               temp_filepath=temp_filepath)

    def _get_cleaner(self, table_name, manifest_row):
        """
        Returns the custom cleaner class that is to be used to clean the 
        specific data for use in database.
        
        :param table_name: the table name for that data being processed
        :param manifest_row: the row representing the data being loaded
        :return: instance of custom cleaner class
        """
        cleaner_class_name = self.meta[table_name]['cleaner']
        return ingestionfunctions.get_cleaner_from_name(
            meta=self.meta,
            manifest_row=manifest_row,
            name=cleaner_class_name,
            engine=self.engine)

    def _get_meta_only_fields(self, table_name, data_fields):
        """
        Returns fields that exist in meta.json but not CSV so we can add 
        them to the row as it is cleaned and written to PSV file.
        
        :param table_name: the table name for the data being processed
        :param data_fields: the fields for the data being processed
        :return: additional fields as dict
        """
        meta_only_fields = {}
        for field in self.meta[table_name]['fields']:
            if field['source_name'] not in data_fields:
                # adds 'sql_name',None as key,value pairs in dict
                meta_only_fields[field['sql_name']] = None
        return meta_only_fields

    def _configure_db_interface(self, manifest_row, temp_filepath):
        """
        Returns an interface object for the sql database
        
        :param manifest_row: a given row in the manifest
        :param temp_filepath: the file path where PSV will be saved
        """
        # check for database manifest - create it if it doesn't exist
        sql_manifest_exists = \
            ingestionfunctions.check_or_create_sql_manifest(engine=self.engine)
        logging.info("sql_manifest_exists: {}".format(sql_manifest_exists))

        # configure database interface object and get matching manifest row
        interface = HISql(meta=self.meta, manifest_row=manifest_row,
                          engine=self.engine, filename=temp_filepath)
        return interface

    def _load_single_file(self, table_name, manifest_row, csv_reader,
                          temp_filepath):
        """
        Cleans the data for the table name in the given manifest row, writes 
        the clean data to PSV file, and then passes on that information so 
        the database can be updated accordingly.
        """
        # get database interface and it's equivalent manifest row
        sql_interface = self._configure_db_interface(
            manifest_row=manifest_row, temp_filepath=temp_filepath)

        sql_manifest_row = sql_interface.get_sql_manifest_row()

        cleaner = self._get_cleaner(table_name=table_name,
                                    manifest_row=manifest_row)
        csv_writer = CSVWriter(meta=self.meta,
                               manifest_row=manifest_row,
                               filename=temp_filepath)

        # clean the file and save the output to a local pipe-delimited file
        # if it doesn't have a 'loaded' status in the database manifest
        if csv_reader.should_file_be_loaded(sql_manifest_row=sql_manifest_row):
            print("  Cleaning...")
            meta_only_fields = self._get_meta_only_fields(
                table_name=table_name, data_fields=csv_reader.keys)
            for idx, data_row in enumerate(csv_reader):
                data_row.update(meta_only_fields)  # insert other field dict
                clean_data_row = cleaner.clean(data_row, idx)
                if clean_data_row is not None:
                    csv_writer.write(clean_data_row)

            csv_writer.close()

            # write the data to the database
            self._update_database(sql_interface=sql_interface)

            if not self._keep_temp_files:
                csv_writer.remove_file()

    def _update_database(self, sql_interface):
        """
        Load the clean PSV file into the database
        """
        print("  Loading...")

        # create table if it doesn't exist
        sql_interface.create_table_if_necessary()
        try:
            sql_interface.write_file_to_sql()
        except TableWritingError:
            # TODO: tell user total count of errors.
            # currently write_file_to_sql() just writes in log that file failed
            self._failed_table_count += 1
            pass


def main(passed_arguments):
    """
    Initializes load procedure based on passed command line arguments and
    options.
    """

    # use real data as default
    scripts_path = os.path.abspath(os.path.join(PYTHON_PATH, 'scripts'))
    meta_path = os.path.abspath(os.path.join(scripts_path, 'meta.json'))
    manifest_path = os.path.abspath(os.path.join(scripts_path, 'manifest.csv'))

    # Locally, we can optionally have sample data
    if passed_arguments.sample and passed_arguments.database != 'remote':
        meta_path = os.path.abspath(os.path.join(scripts_path,
                                                 'meta_sample.json'))
        manifest_path = os.path.abspath(
            os.path.join(scripts_path, 'manifest_sample.csv'))

    # for case of more than one database choice default to the option with
    # the lowest risk if database is updated
    if passed_arguments.database == 'docker':
        database_choice = 'docker_database'
        drop_tables = True

    elif passed_arguments.database == 'docker_local':
        database_choice = 'docker_with_local_python'
        drop_tables = True

    elif passed_arguments.database == 'remote':
        database_choice = 'remote_database'
        drop_tables = False #TODO this is a hacky way to avoid dropping tables because it's not working with RDS...

        # Only users with additional admin privileges can rebuild the
        # remote database
        if not passed_arguments.update_only:
            database_choice = 'remote_database_master'

    # TODO: do we want to default to local or docker?
    elif passed_arguments.database == 'local':
        database_choice = 'local_database'
        drop_tables = True

    # universal defaults
    keep_temp_files = True

    # Instantiate and run the loader
    loader = LoadData(database_choice=database_choice, meta_path=meta_path,
                      manifest_path=manifest_path,
                      keep_temp_files=keep_temp_files,
                      drop_tables=drop_tables)

    if passed_arguments.update_only:
        loader.update_database(passed_arguments.update_only)
    else:
        loader.rebuild()



    #TODO add in failures report here e.g. _failed_table_count

if __name__ == '__main__':
    """
    Continue to honor command line feature after refactoring to encapsulate 
    the module as a class. 
    """

    # configuration: see /logs/example-logging.py for usage examples
    logging.basicConfig(filename=logging_filename, level=logging.DEBUG)
    # Pushes everything from the logger to the command line output as well.
    logging.getLogger().addHandler(logging.StreamHandler())

    description = 'Loads our flat file data into the database of choice. You ' \
                  'can load sample or real data and/or rebuild or update only '\
                  'specific flat files based on unique_data_id values.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("database", help='which database the data should be '
                                         'loaded to',
                        choices=['docker', 'docker-local', 'local', 'remote'])
    parser.add_argument('-s', '--sample', help='load with sample data',
                        action='store_true')
    parser.add_argument('--update-only', nargs='+',
                        help='only update tables with these unique_data_id '
                             'values')

    # handle passed arguments and options
    main(parser.parse_args())
