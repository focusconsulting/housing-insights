"""
Base Api Connection classes.
"""

import csv
import os
from uuid import uuid4

from housinginsights.config.base import HousingInsightsConfig
from housinginsights.sources.models.pres_cat import PROJ_FIELDS, \
    SUBSIDY_FIELDS, PROJ_ADDRE_FIELDS
from housinginsights.tools import dbtools

from housinginsights.sources.base import BaseApiConn
from housinginsights.tools import misc as misctools
from housinginsights.tools.logger import HILogger

logger = HILogger(name=__file__, logfile="proj_sources.log", level=10)


class ProjectBaseApiConn(BaseApiConn):
    """
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
    """
    def __init__(self, baseurl, proxies=None, database_choice=None,
                 debug=False):
        
        if database_choice is None:
            database_choice = 'docker_database'

        super().__init__(baseurl, proxies, database_choice, debug=debug)

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

    def _get_nlihc_id_from_db(self, addresses, uid):
        """
        Returns a tuple (nlihc_id, unique_data_id, in_proj_table_flag,
        found_via, list of mar_ids) for a given address
        id by looking for any matching address or mar_id for the list of
        addresses passed.

        If there isn't a map to an existing building in the table,
        a randomly generated uuid is returned as nlihc_id.
        """
        
        # look for any matching address. If we find a match, assume the
        # whole project is match
        mar_ids = list()
        for address in addresses:

            # first handle non-matching "matches"
            if address in ['others', 'NA', '', ' ', 'Null', None]:
                # not a real match, go to next address
                continue

            # next try lookup by mar id first
            try:
                mar_id = self._get_mar_id(address)
                mar_ids.append(mar_id)
                nlihc_id, unique_data_id = self.proj_addre_lookup_from_mar[
                    mar_id]
                return nlihc_id, unique_data_id, True, 'mar_id', mar_ids
            except KeyError:
                # mar id not in proj_addre table
                pass

            # try the address directly
            try:
                nlihc_id, unique_data_id = self.proj_addre_lookup[
                    address]
                return nlihc_id, unique_data_id, True, 'address', mar_ids
            except KeyError:
                # address not already in data
                continue

        return str(uuid4()), uid, False, None, mar_ids

    def _append_addresses(self, addresses, nlihc_id, addre_writer, line,
                          fields_map):
        """
        Writes the _addre.csv with the same metadata columns as the
        prescat_addre.csv.

        :param addresses: the list of addresses mapping to the given nlihc_id
        :param nlihc_id: the prescat key for the addresses
        :param addre_writer: the file object to be written to
        :param line: the current source row being processed
        :param fields_map: the mapping between source metadata columns and
        prescat_addre metadata columns
        :return: None
        """

        for address in addresses:
            data = dict()
            for field in PROJ_ADDRE_FIELDS:  # populate row columns accordingly
                value = fields_map[field]
                if value is None:  # populate missing fields accordingly
                    if field == 'Nlihc_id':
                        data[field] = nlihc_id
                    elif field == 'Bldg_address_id':
                        data[field] = self._get_mar_id(address)
                    else:
                        data[field] = None
                elif field == 'Bldg_addre':  # use distinct address for address
                    data[field] = address
                else:
                    data[field] = line[value]

            addre_writer.writerow(data)

    def _get_mar_id(self, address):
        """
        Tries a few different methods of turning an address into a mar id, starting
        with the fastest and going to the most robust.
        """
        db_conn = self.engine.connect()

        #Find the mar_id if we can
        if address=='others': #happens often in current prescat
            mar_id = ''
        else:
            try: 
                #Faster, but only works if address is not messy
                mar_id = self.mar_addr_lookup[address.upper()] #MAR uses uppercase
            except KeyError:
                #more robust method has common substitutions and MAR API fallback
                #Will return empty if no match
                mar_id = misctools.check_mar_for_address(addr=address, conn=db_conn)

        return mar_id

    def add_mar_addr_lookup(self):
        """
        Adds an in-memory lookup table of the contents of the MAR
        Key = full address in format 123 M ST NW (all upper case as in MAR)
        value = mar_id
        """

        with self.engine.connect() as conn:
            # do mar_id lookup
            q = "select full_address, mar_id from mar"
            proxy = conn.execute(q)
            result = proxy.fetchall()
            self.mar_addr_lookup = {d[0]: d[1] for d in result}

    def add_proj_addre_lookup(self):
        """
        Adds an in-memory lookup table of the contents of the current
        proj_addre table in the linked database. Used for entity resolution
        """
        with self.engine.connect() as conn:
            # do mar_id lookup
            q = "select address, nlihc_id, unique_data_id from proj_addre"
            proxy = conn.execute(q)
            result = proxy.fetchall()
            self.proj_addre_lookup = {d[0]: (d[1], d[2]) for d in result}

    def add_proj_addre_lookup_from_mar(self):
        """
        Adds an in-memory lookup table of the contents of the current
        proj_addre table but with the mar_id as key instead of address. Used
        for entity resolution.
        """
        with self.engine.connect() as conn:
            # do mar_id lookup
            q = "select mar_id, nlihc_id, unique_data_id from proj_addre"
            proxy = conn.execute(q)
            result = proxy.fetchall()
            self.proj_addre_lookup_from_mar = {d[0]: (d[1], d[2]) for d in
                                               result}

    def create_project_subsidy_csv(self, uid, project_fields_map,
                                   subsidy_fields_map,
                                   proj_addre_fields_map, database_choice=None):
        """
        Writes 'new_proj_data_file' and 'new_subsidy_data_file' raw files
        from the source csv file. It then deletes (maybe not?) the source file so it
        doesn't get added to manifest and loaded into the database.
        """
        db_conn = self.engine.connect()

        # create file path objects
        source_csv = self.output_paths[uid]
        folder = os.path.dirname(source_csv)
        new_proj_data_file = os.path.join(folder, "{}_project.csv".format(uid))
        new_subsidy_data_file = os.path.join(folder, "{}_subsidy.csv".format(uid))
        addre_path = os.path.join(folder, "{}_addre.csv".format(uid))

        # Get lookup data from database
        self.add_proj_addre_lookup()
        self.add_mar_addr_lookup()
        self.add_proj_addre_lookup_from_mar()

        # create dchousing_project/subsidy files from source
        with open(source_csv, encoding='utf-8') as f, \
                open(new_proj_data_file, mode='w', encoding='utf-8') as proj, \
                open(new_subsidy_data_file, mode='w', encoding='utf-8') as subsidy, \
                open(addre_path, mode='w', encoding='utf-8') as addre:

            source_csv_reader = csv.DictReader(f)

            proj_writer = csv.DictWriter(proj, fieldnames=PROJ_FIELDS)
            proj_writer.writeheader()
            subsidy_writer = csv.DictWriter(subsidy, fieldnames=SUBSIDY_FIELDS)
            subsidy_writer.writeheader()
            addre_writer = csv.DictWriter(addre, fieldnames=PROJ_ADDRE_FIELDS)
            addre_writer.writeheader()

            # If the project doesn't exists in the database, we want to add a
            # new record to the project table.
            #
            # All projects need a new record added to the subsidy table. If that
            # project already exists in the database, link it to the project
            # using the nlihc_id; if not, link it to the record that was added
            # to the proj_writer output file."
            for source_row in source_csv_reader:

                try:
                    # get unique addresses for address representing this row
                    # then do a quick standardization clean up
                    addr_field_name = project_fields_map['Proj_addre']
                    address_data = source_row[addr_field_name]
                    addresses = misctools.get_unique_addresses_from_str(address_data)
                    addresses = [misctools.quick_address_cleanup(a) for a in
                                 addresses]

                    # found_via is which method was first successful,
                    # mar_id_found is the mar_id used if it got to the
                    # mar_id phase.
                    nlihc_id, data_id, in_proj_table, found_via, mar_ids_found \
                        = self._get_nlihc_id_from_db(addresses=addresses,
                                                     uid=uid)

                    uid_addre = uid + '_addre'  # correct uid for *_addre

                    logger.info('proj_address lookup result: found= {}, '
                                'via= {}, nlihc_id= {}, '
                                'unique_data_id origin= {}, current uid= {}, '
                                'addresses= {}, mar_ids= {}'.format(
                        in_proj_table, found_via, nlihc_id, data_id, uid_addre,
                        addresses, mar_ids_found))

                    # add values to the project table output file if no match
                    # found or match is found and same uid
                    if not in_proj_table or data_id == uid_addre:
                        data = self._map_data_for_row(nlihc_id=nlihc_id,
                                                      fields=PROJ_FIELDS,
                                                      fields_map=project_fields_map,
                                                      line=source_row)

                        # TODO need to finish this method
                        data = self._geocode_if_needed(data, mar_ids_found)

                        proj_writer.writerow(data)

                        # add all to the proj_addre table
                        # TODO only doing this here means we are assuming that the new source
                        # does not have any additional addresses in its list. Should verify
                        # that is typical. Otherwise, append_addresses will need to double
                        # check that it is not creating duplicate records - which will also
                        # be tricky since we will want duplicates from the same source that
                        # have been loaded into the database previously.

                        # pass '' if address missing
                        if not addresses:
                            addresses = ['']
                        # TODO: probably not a good idea to add with missing
                        # TODO: address metadata - we should consider to mar
                        # TODO: table look up front
                        self._append_addresses(addresses=addresses,
                                               nlihc_id=nlihc_id,
                                               addre_writer=addre_writer,
                                               line=source_row,
                                               fields_map=proj_addre_fields_map)

                    # add all to subsidy table
                    data = self._map_data_for_row(nlihc_id=nlihc_id,
                                                  fields=SUBSIDY_FIELDS,
                                                  fields_map=subsidy_fields_map,
                                                  line=source_row)
                    data = self._add_calculated_subsidy_data(uid, data)
                    subsidy_writer.writerow(data)
                except Exception as e:
                    logger.error("Failed to process {}".format(source_row))
                    if self.debug:
                        raise e

    def _geocode_if_needed(self, data, mar_ids_found):
        '''
        TODO this is incomplete!!!!


        '''
        geocode_fields = [data['Proj_lat'], data['Proj_lon'], data['Zip'],
                          data['Cluster_tr2000'], data['Ward2012']]
        if None in geocode_fields:
            for mar_id in mar_ids_found:
                try:
                    mar_record = 'get_mar_record' #need to lookup from the database mar table
                    #data['Proj_lat'] = mar_record['latitude']
                    break
                except Exception as e:
                    continue

        return data

    def _add_calculated_subsidy_data(self, uid, data):
        """
        Fields that are not directly mapped from their source need to be
        calculated before adding them to the output data. 
        """

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
