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
    def __init__(self,baseurl, proxies=None, database_choice=None):
        
        super().__init__(baseurl,proxies)

        if database_choice is None:
            database_choice = 'docker_database'

        self.engine = dbtools.get_database_engine(database_choice)

        #Get a dict mapping address to mar id from the database and store in memory
        # for use in other methods.
        self.add_mar_addr_lookup()



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

    def create_address_csv_prescat(self,uid,proj_path=None, addre_path=None):
        '''
        Used for the project table only?

        Can't think of a way to make the same function for both prescat (which 
        already has proj/subsidy split) and the other data sets that don't and
        therefore need the address splitting to happen during entity resolution. 

        TODO this is incomplete.
        '''



        with open(proj_path, encoding='utf-8') as proj, \
                open(addre_path, mode='w', encoding='utf-8') as addre:
            proj_reader = csv.DictReader(proj)
            addre_writer = csv.DictWriter(addre, fieldnames=['nlhic_id','address', 'mar_id']) #TODO make this an imported model
            addre_writer.writeheader()

            for proj_row in proj_reader:
                address_data = proj_row['Proj_addre']
                nlihc_id = proj_row['Nlihc_id']

                addresses = misctools.get_unique_addresses_from_str(address_data)

                self._append_addresses(addresses=addresses, nlihc_id = nlihc_id, addre_writer = addre_writer)

    def _append_addresses(self, addresses, nlihc_id, addre_writer):
        
        db_conn = self.engine.connect()

        for address in addresses:
            data = {}
            data['address'] = address
            data['nlhic_id'] = nlihc_id
            
            #Find the mar_id if we can
            if address=='others': #happens often in current prescat
                data['mar_id'] = ''
            else:
                try: 
                    #Faster, but only works if address is not messy
                    data['mar_id'] = self.mar_addr_lookup[address.upper()] #MAR uses uppercase
                except KeyError:
                    #more robust method has common substitutions and MAR API fallback
                    data['mar_id']= misctools.check_mar_for_address(addr=address, conn=db_conn)

            addre_writer.writerow(data)


    def add_mar_addr_lookup(self):
        '''
        
        '''

        with self.engine.connect() as conn:
            # do mar_id lookup
            q = "select full_address, mar_id from mar"
            proxy = conn.execute(q)
            result = proxy.fetchall()
            self.mar_addr_lookup = {d[0]:d[1] for d in result}


    def create_project_subsidy_csv(self, uid, project_fields_map,
                                   subsidy_fields_map, database_choice=None):
        """
        Writes 'new_proj_data_file' and 'new_subsidy_data_file' raw files
        from the source csv file. It then deletes (maybe not?) the source file so it
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
        new_addre_data_file = os.path.join(folder, "{}_addre.csv".format(uid))


        # create dchousing_project/subsidy files from source
        with open(source_csv, encoding='utf-8') as f, \
                open(new_proj_data_file, mode='w', encoding='utf-8') as proj, \
                open(new_subsidy_data_file, mode='w', encoding='utf-8') as subsidy:

            source_csv_reader = csv.DictReader(f)

            proj_writer = csv.DictWriter(proj, fieldnames=PROJ_FIELDS)
            proj_writer.writeheader()
            subsidy_writer = csv.DictWriter(subsidy, fieldnames=SUBSIDY_FIELDS)
            subsidy_writer.writeheader()
            addre_writer = csv.DictWriter(addre, fieldnames=['nlhic_id','address', 'mar_id']) #TODO make this an imported model
            addre_writer.writeheader()


            # If the project doesn't exists in the database, we want to add a
            # new record to the project table.
            #
            # All projects need a new record added to the subsidy table. If that
            # project already exists in the database, link it to the project
            # using the nlihc_id; if not, link it to the record that was added
            # to the proj_writer output file."
            for source_row in source_csv_reader:

                #Split the addresses
                addr_field_name = project_fields_map['Proj_addre'] 
                address_data = source_row[addr_field_name]
                addresses = misctools.get_unique_addresses_from_str(address_data)



                #TODO need to change how we look for matches to use the newly available one to many address list

                #WARNING this code is now broken - need to load the prescat_addre file into database. 



                #Should write this out AFTER we have identified any matching nlihc_id
                self._append_addresses(addresses=addresses, nlihc_id = nlihc_id, addre_writer = addre_writer)




                #TODO the stuff below is what needs to be changed to use new workflow. 

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
