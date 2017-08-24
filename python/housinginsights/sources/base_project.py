"""
Base Api Connection classes.
"""

from urllib.parse import urljoin
from datetime import datetime
from uuid import uuid4

from housinginsights.config.base import HousingInsightsConfig
from housinginsights.sources.models.pres_cat import PROJ_FIELDS, \
    SUBSIDY_FIELDS
from housinginsights.tools import dbtools

import requests
import csv
import os
import logging

from housinginsights.sources.base import BaseApiConn
from housinginsights.tools import misc as misctools

class ProjectBaseApiConn(BaseApiConn):
    '''
    Adds additional methods needed for anything that deals with the project
    table, e.g. the DCHousingApiConn and the DhcdApiConn. Provides
    methods for splitting downloaded data into necessary 'projects'
    and 'subsidy' files. 

    Separated from the base class to avoid circular inheritance with 
    the MarApiConn that we use for entity resolution. 

    TODO could also make this a cleaning step instead of a download
    data step? But this would require refactor due to creation of
    two files from one, while ingestion process is set up with the 
    concept of one file = one table.
    '''

    def _map_data_for_row(self, nlihc_id, fields, fields_map, line):
        """
        Returns a dictionary that represents the values in line mapped to
        those fields in the given fields map.
        :param nlihc_id: the nlihc_id for the current line in dchousing data
        :param fields: the column headers data we want returned
        :param fields_map: a dictionary mapping for the dchousing headers to
        the field headers that should be returned
        :param line: the current line in the dchousing data to be mapped
        """
        data = {}
        for field in fields:
            value = fields_map[field]
            if value is None:
                if field == 'Nlihc_id':
                    data[field] = nlihc_id
                else:
                    data[field] = None
            else:
                data[field] = line[value]

            # NOTE - only needed if using data downloaded from api call
            # instead of batch csv download
            # clean opendata 'GIS_DTTM' formatting - convert milliseconds
            # if value == 'GIS_LAST_MOD_DTTM':
            #     milli_sec = int(line[value])
            #     data[field] = \
            #         datetime.fromtimestamp(milli_sec / 1000.0).strftime(
            #             '%m/%d/%Y')
        return data

    def _get_nlihc_id_from_db(self, db_conn, mar_id):
        """
        Returns a tuple nlihc_id, in_proj_table_flag pair for a given address
        id by performing a lookup on the project table in the database using
        the mar_id column.

        If there doesn't map to an existing building in the table,
        a randomly generated uuid is returned as nlihc_id.
        """
        result = None
        if mar_id != None:
            query = "select nlihc_id from project where mar_id = " \
                    "'{}';".format(mar_id)
            query_result = db_conn.execute(query)
            result = [dict(x) for x in query_result.fetchall()]

        if result:
            return result[0]['nlihc_id'], True
        else:
            return str(uuid4()), False

    def create_project_subsidy_csv(self, uid, project_fields_map,
                                   subsidy_fields_map, database_choice=None):
        """
        Writes 'new_proj_data_file' and 'new_subsidy_data_file' raw files
        from the source csv file. It then deletes the source file so it
        doesn't get added to manifest and loaded into the database.
        """
        if database_choice is None:
            database_choice = 'docker_database'
        engine = dbtools.get_database_engine(database_choice)
        db_conn = engine.connect()

        # create file path objects
        source_csv = self.output_paths[uid]
        folder = os.path.dirname(source_csv)
        new_proj_data_file = os.path.join(folder, "{}_project.csv".format(uid))
        new_subsidy_data_file = os.path.join(folder, "{}_subsidy.csv".format(uid))

        # create dchousing_project/subsidy files from source
        with open(source_csv, encoding='utf-8') as f, \
                open(new_proj_data_file, mode='w', encoding='utf-8') as proj, \
                open(new_subsidy_data_file, mode='w', encoding='utf-8') as subsidy:

            source_csv_reader = csv.DictReader(f)
            proj_writer = csv.DictWriter(proj, fieldnames=PROJ_FIELDS)
            proj_writer.writeheader()
            subsidy_writer = csv.DictWriter(subsidy, fieldnames=SUBSIDY_FIELDS)
            subsidy_writer.writeheader()

            # If the project doesn't exists in the database, we want to add a
            # new record to the project table.
            #
            # All projects need a new record added to the subsidy table. If that
            # project already exists in the database, link it to the project
            # using the nlihc_id; if not, link it to the record that was added
            # to the proj_writer output file."
            for source_row in source_csv_reader:

                #First, perform data-source appropriate transformations to the data
                if uid == 'dhcd_dfd_properties':
                    addr = source_row['address__street_1']
                    
                    #The DHCD data often has multiple addresses separated by semicolon
                    #  for now, let's search only for the first one
                    try:
                        first_semi = addr.index(';')
                        addr = addr[0:first_semi]
                    except ValueError:
                        addr = addr

                    #Assign these updated values to the dictionary
                    source_row['address_single'] = addr
                    source_row['mar_id'] = misctools.check_mar_for_address(addr=addr, conn=db_conn)
                    

                #Try to find the project in the database
                col_options = {'dchousing':'ADDRESS_ID','dhcd_dfd_properties':"mar_id"}
                addr_col = col_options[uid]

                nlihc_id, in_proj_table = self._get_nlihc_id_from_db(
                            db_conn=db_conn, 
                            mar_id=source_row[addr_col])
                
                #for debugging
                if uid == 'dhcd_dfd_properties':
                    print(source_row['mar_id'],source_row['address_single'],'\t',in_proj_table,nlihc_id)
                

                #Add values to the project table output file if necessary
                if not in_proj_table:
                    data = self._map_data_for_row(nlihc_id=nlihc_id,
                                                  fields=PROJ_FIELDS,
                                                  fields_map=project_fields_map,
                                                  line=source_row)
                    proj_writer.writerow(data)

                # add all to subsidy table
                data = self._map_data_for_row(nlihc_id=nlihc_id,
                                              fields=SUBSIDY_FIELDS,
                                              fields_map=subsidy_fields_map,
                                              line=source_row)
                data = self._add_calculated_subsidy_data(uid,data)
                subsidy_writer.writerow(data)

    def _add_calculated_subsidy_data(self, uid,data):
        '''
        Fields that are not directly mapped from their source need to be
        calculated before adding them to the output data. 
        '''

        if uid == 'dhcd_dfd_properties':
            data['Program'] = 'DHCD Quickbase - Unknown'
            data['Portfolio'] = 'DHCD Quickbase - Funding Status Unknown' #Need to get the 'project' table of quickbase working to determine this better

        if uid == 'dchousing':
            data['Portfolio'] = 'DC Government - Unknown' #Not enough info in the source data currently to differentiate. 'Program' has a little more info.

        return data


class BaseApiManager(object):

    classname = "base"

    def __init__(self, config_file):
        self.config = self.get_config(config_file)

    def get_config(self, config_file):
        config = HousingInsightsConfig(config_file)
        return config.get_section(self.__class__.classname)
