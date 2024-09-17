"""
Module implements any changes needed to the data before it arrives in our
database - replacing null, parsing dates, parsing boolean, and handling weird
values.
"""

from abc import ABCMeta, abstractmethod
from datetime import datetime
import dateutil.parser as dateparser
import os
from uuid import uuid4

from housinginsights.ingestion.DataReader import HIReader
from housinginsights.sources.mar import MarApiConn
from housinginsights.sources.models.pres_cat import CLUSTER_DESC_MAP
from housinginsights.sources.google_maps import GoogleMapsApiConn
from housinginsights.sources.models.mar import MAR_TO_TABLE_FIELDS
from housinginsights.tools.logger import HILogger


PYTHON_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
)

logger = HILogger(name=__file__, logfile="ingestion.log")

"""
Usage:
Dynamically import based on name of class in meta.json:
http://stackoverflow.com/questions/4821104/python-dynamic-instantiation-from-string-name-of-a-class-in-dynamically-imported
"""


class CleanerBase(object, metaclass=ABCMeta):
    def __init__(self, meta, manifest_row, cleaned_csv="", removed_csv="", engine=None):
        self.cleaned_csv = cleaned_csv
        self.removed_csv = removed_csv
        self.engine = engine

        self.manifest_row = manifest_row
        self.tablename = manifest_row["destination_table"]
        self.meta = meta
        self.fields = meta[self.tablename]["fields"]  # a list of dicts

        self.null_value = "Null"  # what the SQLwriter expects in the temp csv

        # Flatten the census mapping file so that every potential name of a census tract can be translated to its standard format
        self.census_mapping = {}
        census_reader = HIReader(
            os.path.join(
                PYTHON_PATH,
                "housinginsights/config/crosswalks/DC_census_tract_crosswalk.csv",
            )
        )
        for row in census_reader:
            for key, value in row.items():
                self.census_mapping[value] = row["census_tract"]

        # List of all date fields for parsing purposes
        self.date_fields = []
        for field in self.fields:
            if field["type"] == "date":
                self.date_fields.append(field["source_name"])

    @abstractmethod
    def clean(self, row, row_num):
        # TODO: add replace_null method as required for an implementation (#176)
        pass

    def add_proj_addre_lookup_from_mar(self):
        """
        Adds an in-memory lookup table of the contents of the current
        proj_addre table but with the mar_id as key instead of address. Used for entity resolution
        Result format: {'23105':'NL0000121', '23106':'NL0000223'} i.e. 'mar_id':'nlihc_id'
        """
        with self.engine.connect() as conn:
            # do mar_id lookup
            q = "select mar_id, nlihc_id from proj_addre"
            proxy = conn.execute(q)
            result = proxy.fetchall()
            self.proj_addre_lookup_from_mar = {d[0]: d[1] for d in result}

    def add_ssl_nlihc_lookup(self):
        with self.engine.connect() as conn:
            # do mar_id lookup
            q = "select ssl, nlihc_id from parcel"
            proxy = conn.execute(q)
            result = proxy.fetchall()
            self.ssl_nlihc_lookup = {d[0]: d[1] for d in result}

    def get_nlihc_id_if_exists(self, mar_ids_string, ssl=None):
        "Checks for record in project table with matching MAR id."

        # DC Tax has comma separated list of relevant mar ids
        mar_id_list = mar_ids_string.split(",")
        for mar_id in mar_id_list:
            try:
                # If we find a matching mar_id, assume the whole thing matches
                nlihc_id = self.proj_addre_lookup_from_mar[mar_id]
                return nlihc_id

            except KeyError:
                pass  # keep checking the rest of the list

        # optionally, try searching SSLs - used only for dc tax
        try:
            nlihc_id = self.ssl_nlihc_lookup[ssl]
            return nlihc_id
        except KeyError:
            pass  # means didn't find match

        # If we don't find a match
        return self.null_value

    # TODO: figure out what is the point of this method...it looks incomplete

    def field_meta(self, field):
        for field_meta in self.fields:
            if field_meta["source_name"] == field:
                return field_meta
            return None

    def replace_nulls(self, row, null_values=["NA", "-", "+", "", None]):
        for key, value in row.items():
            if value in null_values:
                row[key] = self.null_value
        return row

    def remove_escape_char(self, row):
        """
        The / character causes problems if it occurs at the end of a row, as it tricks
        the csv file into joining the two columns together. This occured in
        the 2017 building permits. Swapping it out for a similar but safer
        \ character
        """
        for key, value in row.items():
            if isinstance(row[key], str):
                row[key] = row[key].replace("\\", "/")

        return row

    def remove_line_breaks(self, row):
        # TODO see if it's possible to not do this by getting the copy_from to be ok with breaks
        for key in row:
            row[key] = row[key].replace("\r", "__")
            row[key] = row[key].replace("\n", "__")
            row[key] = row[key].replace("|", "__")
        return row

    def format_date(self, value):
        date = None
        try:
            _date = dateparser.parse(value, dayfirst=False, yearfirst=False)
            # _date = datetime.strptime(value, '%m/%d/%Y')
            date = datetime.strftime(_date, "%Y-%m-%d")
        except Exception as e:
            if value is None or value == self.null_value:
                date = self.null_value
            else:
                logger.warning("    Unable to format date properly: {}".format(value))
                date = self.null_value

        return date

    def convert_boolean(self, value):
        mapping = {
            "Yes": True,
            "No": False,
            "Y": True,
            "N": False,
            "TRUE": True,
            "FALSE": False,
            "1": True,
            "0": False,
            "": self.null_value,
        }
        try:
            return mapping[value]
        except:
            return False

    def parse_dates(self, row):
        """
        Tries to automatically parse all dates that are of type:'date' in the meta
        """
        for source_name in self.date_fields:
            row[source_name] = self.format_date(row[source_name])
        return row

    def remove_non_dc_tracts(self, row, column_name):
        """
        TODO change to use self.census_mapping
        """
        dc_tracts = [
            "11001000100",
            "11001000201",
            "11001000202",
            "11001000300",
            "11001000400",
            "11001000501",
            "11001000502",
            "11001000600",
            "11001000701",
            "11001000702",
            "11001000801",
            "11001000802",
            "11001000901",
            "11001000902",
            "11001001001",
            "11001001002",
            "11001001100",
            "11001001200",
            "11001001301",
            "11001001302",
            "11001001401",
            "11001001402",
            "11001001500",
            "11001001600",
            "11001001702",
            "11001001803",
            "11001001804",
            "11001001901",
            "11001001902",
            "11001002001",
            "11001002002",
            "11001002101",
            "11001002102",
            "11001002201",
            "11001002202",
            "11001002301",
            "11001002302",
            "11001002400",
            "11001002501",
            "11001002502",
            "11001002600",
            "11001002701",
            "11001002702",
            "11001002801",
            "11001002802",
            "11001002900",
            "11001003000",
            "11001003100",
            "11001003200",
            "11001003301",
            "11001003302",
            "11001003400",
            "11001003500",
            "11001003600",
            "11001003700",
            "11001003800",
            "11001003900",
            "11001004001",
            "11001004002",
            "11001004100",
            "11001004201",
            "11001004202",
            "11001004300",
            "11001004400",
            "11001004600",
            "11001004701",
            "11001004702",
            "11001004801",
            "11001004802",
            "11001004901",
            "11001004902",
            "11001005001",
            "11001005002",
            "11001005201",
            "11001005301",
            "11001005500",
            "11001005600",
            "11001005800",
            "11001005900",
            "11001006202",
            "11001006400",
            "11001006500",
            "11001006600",
            "11001006700",
            "11001006801",
            "11001006802",
            "11001006804",
            "11001006900",
            "11001007000",
            "11001007100",
            "11001007200",
            "11001007301",
            "11001007304",
            "11001007401",
            "11001007403",
            "11001007404",
            "11001007406",
            "11001007407",
            "11001007408",
            "11001007409",
            "11001007502",
            "11001007503",
            "11001007504",
            "11001007601",
            "11001007603",
            "11001007604",
            "11001007605",
            "11001007703",
            "11001007707",
            "11001007708",
            "11001007709",
            "11001007803",
            "11001007804",
            "11001007806",
            "11001007807",
            "11001007808",
            "11001007809",
            "11001007901",
            "11001007903",
            "11001008001",
            "11001008002",
            "11001008100",
            "11001008200",
            "11001008301",
            "11001008302",
            "11001008402",
            "11001008410",
            "11001008701",
            "11001008702",
            "11001008802",
            "11001008803",
            "11001008804",
            "11001008903",
            "11001008904",
            "11001009000",
            "11001009102",
            "11001009201",
            "11001009203",
            "11001009204",
            "11001009301",
            "11001009302",
            "11001009400",
            "11001009501",
            "11001009503",
            "11001009504",
            "11001009505",
            "11001009507",
            "11001009508",
            "11001009509",
            "11001009601",
            "11001009602",
            "11001009603",
            "11001009604",
            "11001009700",
            "11001009801",
            "11001009802",
            "11001009803",
            "11001009804",
            "11001009807",
            "11001009810",
            "11001009811",
            "11001009901",
            "11001009902",
            "11001009903",
            "11001009904",
            "11001009905",
            "11001009906",
            "11001009907",
            "11001010100",
            "11001010200",
            "11001010300",
            "11001010400",
            "11001010500",
            "11001010600",
            "11001010700",
            "11001010800",
            "11001010900",
            "11001011000",
            "11001011100",
        ]
        if row[column_name] in dc_tracts:
            return row
        else:
            return None

    def rename_census_tract(self, row, column_name="census_tract"):
        """
        Make all census tract names follow a consistent format.
        column_name corresponds to the key of the row, which depends on
        the source file column name which may be different from the final
        consistent name of census_tract
        """
        # deal with null values
        if row[column_name] == self.null_value:
            return row
        elif row[column_name] in self.census_mapping:
            row[column_name] = self.census_mapping[row[column_name]]
            return row
        else:
            return row

    def replace_tracts(self, row, row_num, column_name="census_tract"):
        """
        Converts the raw census tract code to the more readable format used by PresCat
        """
        current = row[column_name]
        try:
            row[column_name] = self.census_mapping[current]
        except KeyError:
            pass
            # this prints error for many rows with nulls.
            logger.warning("  no matching Tract found for row {}".format(row_num, row))
        return row

    def append_tract_label(self, row, row_num, column_name="census_tract_number"):
        """
        Appends the value 'Tract ' to the raw numeric value in 'census_tract_number' in order to make the value
        consistent with the more readable format used by PresCat
        """
        current = row[column_name]
        try:
            row[column_name] = "Tract " + str(current)
        except KeyError:
            pass
            # this prints error for many rows with nulls.
            logger.warning("  no matching Tract found for row {}".format(row_num, row))
        return row

    def rename_ward(self, row, ward_key="WARD"):
        """
        Standardize ward field to be 'Ward #' - where # represents the numeric
        ward value.
        :param row: the current data row to be cleaned
        :param ward_key: optional parameter for specifying ward field name
        :return: cleaned row data
        """
        if row[ward_key] == self.null_value:
            return row
        else:
            ward = row[ward_key]
            if ward.isnumeric():  # add text if only number
                row[ward_key] = "Ward " + str(ward)
            else:  # make sure text is 'Ward #'
                row[ward_key] = ward.lower().capitalize()
            return row

    def rename_status(self, row):
        """
        Standardize status field to have first letter capitalized and
        remaining letters lowercase.
        """
        row["Status"] = row["Status"].lower().capitalize()
        return row

    def add_mar_id(self, row, address_id_col_name="ADDRESS_ID"):
        """
        Returns the updated row after the mar_id column in the project table
        has been populated with valid value.

        The process involves using address id, lat/lon, or x/y-coords to
        identify mar equivalent address id.
        """
        # api lookup with lat/lon or x/y coords if address id is null or invalid
        mar_api = MarApiConn()
        lat = row["Proj_lat"]
        lon = row["Proj_lon"]
        x_coord = row["Proj_x"]
        y_coord = row["Proj_y"]
        address = row["Proj_addre"]

        # using mar api lookup instead of mar.csv because too slow - see to do^
        proj_address_id = row[address_id_col_name]

        # TODO this is odd, find out why we have both ADDRESS_ID column and mar_id column
        if proj_address_id != self.null_value:
            row["mar_id"] = proj_address_id
            return row
        #    result = mar_api.reverse_address_id(aid=proj_address_id)
        #    return_data_set = result['returnDataset']
        #    if 'Table1' in return_data_set:
        #        row['mar_id'] = return_data_set['Table1'][0]["ADDRESS_ID"]
        #        return row

        result = None  # track result from reverse lookup api calls

        if lat != self.null_value and lon != self.null_value:
            result = mar_api.reverse_lat_lng_geocode(latitude=lat, longitude=lon)
            if result:
                row["mar_id"] = result["Table1"][0]["ADDRESS_ID"]

        elif x_coord != self.null_value and y_coord != self.null_value:
            result = mar_api.reverse_geocode(xcoord=x_coord, ycoord=y_coord)
            if result:
                row["mar_id"] = result["Table1"][0]["ADDRESS_ID"]

        elif address != self.null_value:
            # check whether address is valid - it has street number
            try:
                str_num = address.split(" ")[0]
                int(str_num)
                first_address = address.split(";")[0]
                result = mar_api.find_addr_string(first_address)
            except ValueError:
                logger.info(
                    "ValueError in Mar for {} - returning none".format(
                        row["Proj_addre"]
                    )
                )
                result = None

            if result:
                # Handle case of mar_api returning something but it not being an address
                if (
                    result["returnDataset"] == None
                    or result["returnDataset"] == {}
                    or result["sourceOperation"] == "DC Intersection"
                ):

                    result = None

                if result:
                    row["mar_id"] = result["returnDataset"]["Table1"][0]["ADDRESS_ID"]

        return row

    def add_geocode_from_mar(self, row):
        """
        Uses mar api lookup to populate geographic zones are missing for
        buildings in the project table. The following zones are validated:

        ward
        neighborhood_cluster (e.g. 'cluster 1'
        neighborhood_cluster_desc (eg. 'woodley park and zoo')
        zip
        anc
        census_tract
        status
        """
        # populate proj_city & proj_st accordingly
        if row["Proj_City"] == self.null_value:
            row["Proj_City"] = "Washington"

        if row["Proj_ST"] == self.null_value:
            row["Proj_ST"] = "DC"

        # don't do anything if mar_id doesn't exist for the building
        # this is assuming 'add_mar_id' was called first
        if row["mar_id"] == self.null_value:
            return row

        ward = row["Ward2022"]
        neighbor_cluster = row["cluster2017"]
        neighborhood_cluster_desc = row["cluster2017_name"]
        zipcode = row["Proj_zip"]
        anc = row["Anc2012"]
        census_tract = row["Geo2020"]
        status = row["Status"]
        full_address = row["Proj_addre"]
        image_url = row["Proj_image_url"]
        street_view_url = row["Proj_streetview_url"]
        psa = row["Psa2012"]
        latitude = row["Proj_lat"]
        longitude = row["Proj_lon"]

        # only do mar api lookup if we have a null geocode value
        if self.null_value in [
            ward,
            neighbor_cluster,
            neighborhood_cluster_desc,
            zipcode,
            anc,
            census_tract,
            status,
            full_address,
            image_url,
            street_view_url,
            psa,
            latitude,
            longitude,
        ]:

            try:
                mar_api = MarApiConn()
                result = mar_api.reverse_address_id(aid=row["mar_id"])
                result = result["returnDataset"]["Table1"][0]
            except KeyError:
                return row

        # if there were no null values in the geocodable fields
        else:
            return row

        # update missing geocode values accordingly
        if ward == self.null_value:
            row["Ward2022"] = result["WARD"].lower().capitalize()

        if neighbor_cluster == self.null_value:
            cluster = result["CLUSTER_"]
            if cluster is not None:
                row["Cluster_tr2000"] = cluster

        if neighborhood_cluster_desc == self.null_value:
            row["Cluster_tr2000_name"] = CLUSTER_DESC_MAP.get(
                row["Cluster_tr2000"], self.null_value
            )

        if zipcode == self.null_value:
            zip_code = result["ZIPCODE"]
            row["Proj_zip"] = zip_code
            row["Zip"] = "ZIP " + str(zip_code)

        if anc == self.null_value:
            row["Anc2012"] = result["ANC_2012"]

        if census_tract == self.null_value:
            row["Geo2020"] = result["CENSUS_TRACT"]

        if status == self.null_value:
            row["Status"] = result["STATUS"]

        if full_address == self.null_value:
            row["Proj_addre"] = result["FULLADDRESS"]

        if street_view_url == self.null_value:
            street_view_url = result["STREETVIEWURL"]
            if street_view_url is not None:
                row["Proj_streetview_url"] = street_view_url
            else:
                # TODO - should be able to search for lat/lon from the
                #   address if they are not available here
                # print(row)
                if (
                    row["Proj_lat"] != self.null_value
                    and row["Proj_lon"] != self.null_value
                ):
                    map_api = GoogleMapsApiConn()
                    map_api_result = map_api.check_street_view(
                        row["Proj_lat"], row["Proj_lon"]
                    )

                    if map_api_result:
                        # create street view url per google maps api specs
                        loc_data = map_api_result["Location"]
                        latitude = loc_data["original_lat"]
                        longitude = loc_data["original_lng"]
                        pano_id = loc_data["panoId"]
                        url = map_api.get_street_view_url(latitude, longitude, pano_id)
                        row["Proj_streetview_url"] = url

        if image_url == self.null_value:
            try:
                img_url = result["IMAGEURL"]
                img_dir = result["IMAGEDIR"]
                img_name = result["IMAGENAME"]
                row["Proj_image_url"] = "{}/{}/{}".format(img_url, img_dir, img_name)
            except KeyError:
                row["Proj_image_url"] == self.null_value

        if psa == self.null_value:
            psa = result["PSA"]
            if psa is not None:
                row["Psa2012"] = "PSA " + psa.split(" ")[-1]

        if longitude == self.null_value or latitude == self.null_value:
            latitude = result["LATITUDE"]
            longitude = result["LONGITUDE"]
            if latitude is not None and longitude is not None:
                row["Proj_lat"] = latitude
                row["Proj_lon"] = longitude

        return row

    def add_state_county_to_tract(self):
        pass

    def add_mar_full_lookup(self):
        """
        Adds the self.mar_full_lookup dictionary to the object
        that calls this function. Used in __init__ of any cleaner
        that will need this mar geocoding available.

        Unlike mar_tract_lookup, stores all of the geocode
        fields used by the project table.

        NOTE This is currently unused - realized that the opendata.dc.gov
        MAR does not provide street view url or image urls. To recreate
        streetviewurl, we need another MAR API call so using this method
        does not save us any geocoding time. Saving here for future
        use if other things need more extensive geocoding.
        """

        with self.engine.connect() as conn:
            # do mar_id lookup
            q = """
                select mar_id
                    , ward
                    , neighborhood_cluster
                    , zipcode
                    , anc
                    , census_tract
                    , status
                    , full_address
                    , psa 
                from mar
                """
            proxy = conn.execute(q)
            result = proxy.fetchall()
            self.mar_full_lookup = {d[0]: d[1:] for d in result}

            # Create a mapping of the tuple order to the MAR API key names, so
            # that we can decode the results to look like MAR API results
            self.mar_full_lookup_order = {
                "WARD": 0,
                "CLUSTER_": 1,
                "ZIPCODE": 2,
                "ANC_2012": 3,
                "CENSUS_TRACT": 4,
                "STATUS": 5,
                "FULLADDRESS": 6,
                "PSA": 7,
                "STREETVIEWURL": 8,
            }

    def add_mar_tract_lookup(self):
        """
        Adds the self.mar_tract_lookup dictionary to the object
        that calls this function. Typically called in the __init__
        function of a class that will use this lookup table while
        cleaning
        """

        with self.engine.connect() as conn:
            # do mar_id lookup
            q = "select mar_id, census_tract from mar"
            proxy = conn.execute(q)
            result = proxy.fetchall()
            self.mar_tract_lookup = {d[0]: d[1] for d in result}

    def add_census_tract_from_mar(
        self,
        row,
        column_name="mar_id",
        lat_lon_col_names=("LATITUDE", "LONGITUDE"),
        x_y_coords_col_names=("X", "Y"),
        address_col_name="FULL_ADDRESS",
    ):
        """Returns the census tract for given mar_id using the mar api."""

        mar_id = row[column_name]
        if mar_id == "-100":
            # Some rows in the building permit extract have this as a MAR ID which is known to not be valid
            return row
        # Try to get it from memory first
        try:
            tract = self.mar_tract_lookup[mar_id]
            row["census_tract"] = tract
            return row
        except KeyError:
            pass

        # Then check internal database directly
        with self.engine.connect() as conn:
            # do mar_id lookup
            q = "select census_tract from mar where mar_id = '{}'".format(mar_id)
            proxy = conn.execute(q)
            result = proxy.fetchall()
            if result:
                row["census_tract"] = result.pop()[0]
                return row

            # do lat/lon lookup
            lat = row[lat_lon_col_names[0]]
            lon = row[lat_lon_col_names[1]]
            q = """select census_tract from mar 
            where latitude = {} and longitude = {};""".format(
                lat, lon
            )
            proxy = conn.execute(q)
            result = proxy.fetchall()
            if result:
                row["census_tract"] = result.pop()[0]
                return row

            # do x/y-coord lookup
            xcoord = row[x_y_coords_col_names[0]]
            ycoord = row[x_y_coords_col_names[1]]
            q = """select census_tract from mar 
                where xcoord = {} and ycoord = {};""".format(
                xcoord, ycoord
            )
            proxy = conn.execute(q)
            result = proxy.fetchall()
            if result:
                row["census_tract"] = result.pop()[0]
                return row

            # mar api look up for missing data
            mar_api = MarApiConn()
            result = mar_api.reverse_address_id(aid=row[column_name])

            if result["returnDataset"]:
                geocode_result = result["returnDataset"]["Table1"][0]

                # #  map mar table field names to api result field and values
                # table_map = dict()
                # for key, value in geocode_result.items():
                #     col_name = MAR_TO_TABLE_FIELDS[key]
                #     table_map[col_name] = value

                # prepare new data for inserting into mar table
                col = ["unique_data_id", "mar_id", "id"]
                val = ["mar", mar_id, uuid4()]

                for key, value in geocode_result.items():
                    col.append(MAR_TO_TABLE_FIELDS[key])
                    val.append(value)

                # derive column and values string needed for sql query
                col = ", ".join(col)
                val = ", ".join(val)

                # insert into mar table
                q = "INSERT INTO mar ({cols}) VALUES ({vals})".format(
                    cols=col, vals=val
                )
                conn.execute(q)

                row["census_tract"] = "11001" + str(geocode_result["CENSUS_TRACT"])
                return row
            else:
                # don't repeat api call again if mar_id returns empty data
                q = """INSERT INTO mar (unique_data_id, mar_id, id) VALUES
                ('mar', {}, '{}')""".format(
                    mar_id, uuid4()
                )
                conn.execute(q)

                return row

    def filter_row_by(self, row, criteria=None):
        """
        Returns empty dict for rows that meet filter criteria.

        :param row: the row to be verified
        :param criteria: dict where each key is a field in the row dict and the
        values for which you want filter for. The values for each key should
        be a list of values you don't want to get loaded into the database.
        """
        if criteria is not None:
            for key in criteria:
                if row[key] in criteria[key]:
                    return dict()

        return row


#############################################
# Custom Cleaners
#############################################

# TODO: maybe automate this via cmd line by passing simple list of keys that
# TODO: map to specific cleaner methods including option to pass custom methods


class GenericCleaner(CleanerBase):
    def clean(self, row, row_num=None):
        row = self.replace_nulls(row, null_values=["N", "NA", "", None])
        return row


class ProjectCleaner(CleanerBase):
    def clean(self, row, row_num=None):
        row = self.replace_nulls(row, null_values=["N", "", None])
        row = self.parse_dates(row)

        # TODO need to better handle errors within these, i.e. the MAR API failing
        try:
            row = self.add_mar_id(row, "Proj_address_id")
            row = self.add_geocode_from_mar(row=row)
        except Exception as e:
            logger.error("Error geocoding {}, error was {}".format(row, e))

        row = self.rename_ward(row, ward_key="Ward2022")
        row = self.rename_status(row)
        row = self.rename_census_tract(row, column_name="Geo2020")
        return row


class SubsidyCleaner(CleanerBase):
    def clean(self, row, row_nume=None):
        row["Subsidy_Active"] = self.convert_boolean(row["Subsidy_Active"])
        row["POA_end_actual"] = (
            self.null_value if row["POA_end_actual"] == "U" else row["POA_end_actual"]
        )
        row = self.replace_nulls(row, null_values=["N", "", None])
        row = self.parse_dates(row)
        return row


class TopaOutcomeCleaner(CleanerBase):
    def clean(self, row, row_nume=None):
        row["has_topa_outcome"] = self.convert_boolean(row["has_topa_outcome"])
        row["d_cbo_dhcd_received_ta_reg"] = self.convert_boolean(
            row["d_cbo_dhcd_received_ta_reg"]
        )
        row["TA_assign_rights"] = self.convert_boolean(row["TA_assign_rights"])
        row["d_le_coop"] = self.convert_boolean(row["d_le_coop"])
        row["d_purch_condo_coop"] = self.convert_boolean(row["d_purch_condo_coop"])
        row["d_other_condo"] = self.convert_boolean(row["d_other_condo"])
        row["d_lihtc"] = self.convert_boolean(row["d_lihtc"])
        row["d_dc_hptf"] = self.convert_boolean(row["d_dc_hptf"])
        row["d_dc_other"] = self.convert_boolean(row["d_dc_other"])
        row["d_fed_aff"] = self.convert_boolean(row["d_fed_aff"])
        row["d_rent_control"] = self.convert_boolean(row["d_rent_control"])
        row["d_affordable"] = self.convert_boolean(row["d_affordable"])
        row["d_100pct_afford"] = self.convert_boolean(row["d_100pct_afford"])
        row["d_rehab"] = self.convert_boolean(row["d_rehab"])
        row["d_cbo_involved"] = self.convert_boolean(row["d_cbo_involved"])
        row["d_buyout_100"] = self.convert_boolean(row["d_buyout_100"])
        row["d_buyout_partial"] = self.convert_boolean(row["d_buyout_partial"])

        if row["u_sale_date"] == "":
            row["u_sale_date"] = self.null_value

        return row


class BuildingPermitsCleaner(CleanerBase):
    def __init__(self, meta, manifest_row, cleaned_csv="", removed_csv="", engine=None):
        super().__init__(meta, manifest_row, cleaned_csv, removed_csv, engine)
        self.add_mar_tract_lookup()
        self.add_ssl_nlihc_lookup()

    def clean(self, row, row_num=None):

        row = self.replace_nulls(row, null_values=["NONE", "", None])
        row = self.parse_dates(row)
        row = self.remove_line_breaks(row)
        row = self.rename_cluster(row)
        row = self.rename_ward(row)
        row = self.add_census_tract_from_mar(row, column_name="MARADDRESSREPOSITORYID")
        row = self.remove_escape_char(row)
        return row

    def rename_cluster(self, row):
        if row["NEIGHBORHOODCLUSTER"] == self.null_value:
            return row
        else:
            row["NEIGHBORHOODCLUSTER"] = "Cluster " + str(row["NEIGHBORHOODCLUSTER"])
            return row


class CensusCleaner(CleanerBase):
    def clean(self, row, row_num=None):
        # TODO - use self.rename_census_tract()
        row["census_tract"] = "" + row["state"] + row["county"] + row["tract"]
        # Note, we are losing data about statistical issues. Would be better to copy these to a new column.
        row = self.replace_nulls(
            row, null_values=["N", "**", "***", "****", "*****", "(X)", "-", "", None]
        )
        return row

    def high_low_rent(self, row):
        """
        Rent higher than the max reportable value are suppressed
        e.g: instead of being reported as "3752", a plus sign is added
        and the values over the max value are suppressed eg. "3,500+"
        Rent lower than the lowest reportable is similar (e.g. "100-")
        We assume that the actual value is the max value, and strip out the , and +
        """
        if row["HD01_VD01"][-1] == "+":
            row["HD01_VD01"] = row["HD01_VD01"].replace(",", "")
            row["HD01_VD01"] = row["HD01_VD01"].replace("+", "")
        if row["HD01_VD01"][-1] == "-":
            row["HD01_VD01"] = row["HD01_VD01"].replace(",", "")
            row["HD01_VD01"] = row["HD01_VD01"].replace("-", "")
        return row


class CensusTractToNeighborhoodClusterCleaner(CleanerBase):
    def clean(self, row, row_num=None):
        return row


class CensusTractToWardCleaner(CleanerBase):
    def clean(self, row, row_num=None):
        return row


class CrimeCleaner(CleanerBase):
    def clean(self, row, row_num=None):
        row = self.replace_nulls(row, null_values=["", None])
        row = self.parse_dates(row)
        row = self.replace_tracts(row, row_num, column_name="CENSUS_TRACT")
        row = self.rename_ward(row)
        return row


class DCTaxCleaner(CleanerBase):
    def __init__(self, meta, manifest_row, cleaned_csv="", removed_csv="", engine=None):
        # Call the parent method and pass all the arguments as-is
        super().__init__(meta, manifest_row, cleaned_csv, removed_csv, engine)
        self.add_proj_addre_lookup_from_mar()
        self.add_ssl_nlihc_lookup()

    def clean(self, row, row_num=None):

        row = self.replace_nulls(row, null_values=["", "\\", None])
        row["CITYSTZIP"] = (
            self.null_value if row["CITYSTZIP"] == "," else row["CITYSTZIP"]
        )
        row["VACLNDUSE"] = self.convert_boolean(row["VACLNDUSE"].capitalize())
        row = self.parse_dates(row)
        nlihc_id = self.get_nlihc_id_if_exists("", row["SSL"])
        row["nlihc_id"] = nlihc_id

        return row


class hmda_cleaner(CleanerBase):
    def clean(self, row, row_num=None):
        row = self.replace_nulls(row, null_values=["", None])
        row = self.parse_dates(row)
        row = self.append_tract_label(row, row_num, column_name="census_tract_number")
        return row


class WmataDistCleaner(CleanerBase):
    def clean(self, row, row_num=None):
        return row


class WmataInfoCleaner(CleanerBase):
    def clean(self, row, row_num=None):
        return row


class CharterSchoolsCleaner(CleanerBase):
    def clean(self, row, row_num=None):
        criteria = {"ADDRID": [""], "OBJECTID": [""]}
        row = self.filter_row_by(row, criteria)
        if not row:  # skip other cleaning steps if filtered out
            return None
        row["LEA_ID"] = -1 if row["LEA_ID"] == "" else row["LEA_ID"]
        row["ENROLLMENT"] = 0 if row["ENROLLMENT"] == "" else row["ENROLLMENT"]
        row["AUTHORIZAT"] = 0 if row["AUTHORIZAT"] == "" else row["AUTHORIZAT"]
        row["SCHOOLCODE"] = 0 if row["SCHOOLCODE"] == "" else row["SCHOOLCODE"]
        return row


class reac_score_cleaner(CleanerBase):
    def clean(self, row, row_num=None):
        row = self.replace_nulls(row, null_values=["", None])
        return row


class real_property_cleaner(CleanerBase):
    def clean(self, row, row_num=None):
        row = self.replace_nulls(row, null_values=["", None])
        return row


class dchousing_cleaner(CleanerBase):
    def clean(self, row, row_num=None):
        row = self.replace_nulls(row, null_values=["", None])

        # convert milliseconds to m/d/Y date format
        source_name = "GIS_LAST_MOD_DTTM"
        milli_sec = int(row[source_name])
        row[source_name] = datetime.fromtimestamp(milli_sec / 1000.0).strftime(
            "%m/%d/%Y"
        )

        return row


class TopaCleaner(CleanerBase):
    def __init__(self, meta, manifest_row, cleaned_csv="", removed_csv="", engine=None):
        # Call the parent method and pass all the arguments as-is
        super().__init__(meta, manifest_row, cleaned_csv, removed_csv, engine)
        self.add_proj_addre_lookup_from_mar()
        self.add_ssl_nlihc_lookup()

    def clean(self, row, row_num=None):
        # 2015 dataset provided by Urban Institute as provided in S3 has errant '\'
        # character in one or two columns.  Leave here for now.
        row = self.replace_nulls(row, null_values=["", "\\", None])
        nlihc_id = self.get_nlihc_id_if_exists(row["ADDRESS_ID"])
        row["nlihc_id"] = nlihc_id
        return row


class Zone_HousingUnit_Bedrm_Count_cleaner(CleanerBase):
    def clean(self, row, row_num=None):

        if row["zone_type"] == "census_tract":
            row = self.rename_census_tract(row, column_name="zone")

        return row


class ProjectAddressCleaner(CleanerBase):
    def clean(self, row, row_num=None):
        row = self.replace_nulls(row)
        return row


class ZillowCleaner(CleanerBase):
    """
    Incomplete Cleaner - adding data to the code so we have it when needed (was doing analysis on this)
    """

    def __init__(self, meta, manifest_row, cleaned_csv="", removed_csv=""):
        # Call the parent method and pass all the arguments as-is
        super().__init__(meta, manifest_row, cleaned_csv, removed_csv)

        # These are the 28 zips defined by NeighborhoodInfoDC as the 'primary' zip codes.
        # Not all are available in Zillow data, so want to insert Nulls for any others.
        self._possible_zips = [
            "20001",
            "20002",
            "20003",
            "20004",
            "20005",
            "20006",
            "20007",
            "20008",
            "20009",
            "20010",
            "20011",
            "20012",
            "20015",
            "20016",
            "20017",
            "20018",
            "20019",
            "20020",
            "20024",
            "20032",
            "20036",
            "20037",
            "20052",
            "20057",
            "20059",
            "20064",
            "20332",
            "20336",
        ]

        # All possible neighborhoods as defined here: https://www.zillow.com/howto/api/neighborhood-boundaries.htm
        # Again, data is not available for all neighborhoods.
        self._possible_neighborhoods = [
            "Barnaby Woods",
            "Bellevue",
            "Benning",
            "Chevy Chase",
            "Dupont Park",
            "Eastland Gardens",
            "Foxhall",
            "Ivy City",
            "Judiciary Square",
            "Manor Park",
            "Marshall Heights",
            "Benning Heights",
            "Capitol Hill",
            "Cathedral Heights",
            "Chinatown",
            "Colony Hill",
            "U Street Corridor",
            "Crestwood",
            "Edgewood",
            "Forest Hills",
            "Fort Dupont",
            "Friendship Heights",
            "Gateway",
            "Hawthorne",
            "Kent",
            "Lincoln Heights",
            "Mount Pleasant",
            "Park View",
            "Potomac Heights",
            "Shaw",
            "Tenleytown",
            "Twining",
            "Observatory Circle",
            "Wakefield",
            "Langston",
            "Brightwood Park",
            "Brookland",
            "Buena Vista",
            "Stronghold",
            "Sursum Corda Cooperative",
            "Benning Ridge",
            "Mahaning Heights",
            "Barry Farm",
            "Carver",
            "Burleith",
            "Columbia Heights",
            "Congress Heights",
            "Fairfax Village",
            "Fairlawn",
            "Foggy Bottom",
            "Glover Park",
            "Good Hope",
            "Greenway",
            "Langdon",
            "Ledroit Park",
            "Mount Vernon Square",
            "Naylor Gardens",
            "North Cleveland Park",
            "North Michigan Park",
            "River Terrace",
            "The Palisades",
            "Trinidad",
            "Truxton Circle",
            "Berkley",
            "Brentwood",
            "National Arboretum",
            "National Mall - West Potomac Park",
            "Lady Bird Johnson Park",
            "Gallaudet",
            "Barney Circle",
            "Near Northeast",
            "Penn Quarter",
            "Southwest Federal Center",
            "Knox Hill",
            "Woodlands",
            "Blue Plains Treatment Plant",
            "Woodland-Normanstone Terrace",
            "Pleasant Plains",
            "Burrville",
            "Civic Betterment",
            "East Corner",
            "Hillbrook",
            "Adams Morgan",
            "Anacostia",
            "Bloomingdale",
            "Brightwood",
            "Capitol View",
            "Cleveland Park",
            "Colonial Village",
            "Deanwood",
            "Dupont Circle",
            "Eckington",
            "Fort Davis",
            "Garfield Heights",
            "Georgetown",
            "Hillcrest",
            "Kenilworth",
            "Kingman Park",
            "Theodore Roosevelt Island",
            "Mayfair",
            "Woodridge",
            "Woodley Park",
            "Anacostia Naval Station - Boiling Air Force Base",
            "Navy Yard",
            "Fort Totten",
            "Massachusetts Heights",
            "Downtown",
            "Fort Lincoln",
            "West End",
            "Wesley Heights",
            "Washington Highlands",
            "Spring Valley",
            "Shipley Terrace",
            "Petworth",
            "Penn Branch",
            "Logan Circle",
            "McLean Gardens",
            "Michigan Park",
            "Randle Highlands",
            "Riggs Park",
            "Shepherd Park",
            "Kalorama",
            "Takoma",
            "American University Park",
            "Catholic University",
            "Southwest Waterfront",
            "East Potomac Park",
            "Sixteenth Street Heights",
            "Pleasant Hill",
            "NoMa",
            "Swampoodle",
            "Skyland",
            "Douglas",
            "Arboretum",
            "Fort Davis",
            "Shipley Terrace",
            "Saint Elizabeths",
        ]

        # Same as above, but this is the 'RegionID' as defined by Zillow.
        self._possible_neighborhood_ids = [
            "121672",
            "121674",
            "121675",
            "121689",
            "121705",
            "121708",
            "121724",
            "121739",
            "121740",
            "121755",
            "121756",
            "121676",
            "121685",
            "121687",
            "121692",
            "121696",
            "275794",
            "121701",
            "121710",
            "121717",
            "121719",
            "121726",
            "121728",
            "121735",
            "121744",
            "121751",
            "121762",
            "121771",
            "121776",
            "121785",
            "121794",
            "121801",
            "268821",
            "268832",
            "403482",
            "121680",
            "121681",
            "121682",
            "403484",
            "403491",
            "403493",
            "403498",
            "403500",
            "403507",
            "121683",
            "121697",
            "121698",
            "121713",
            "121714",
            "121716",
            "121731",
            "121732",
            "121733",
            "121748",
            "121750",
            "121763",
            "121764",
            "121765",
            "121767",
            "121780",
            "121797",
            "121799",
            "121800",
            "268801",
            "268803",
            "268819",
            "403137",
            "403138",
            "403485",
            "403486",
            "403487",
            "403488",
            "403489",
            "403502",
            "403503",
            "403504",
            "403479",
            "403480",
            "403494",
            "403495",
            "403496",
            "403497",
            "121668",
            "121670",
            "121677",
            "121679",
            "121686",
            "121693",
            "121695",
            "121702",
            "121704",
            "121709",
            "121718",
            "121727",
            "121729",
            "121736",
            "121743",
            "121745",
            "403135",
            "403134",
            "121816",
            "121815",
            "403139",
            "403116",
            "273767",
            "403478",
            "273489",
            "268811",
            "121808",
            "121807",
            "121806",
            "121791",
            "121788",
            "121774",
            "121772",
            "121754",
            "121759",
            "121761",
            "121777",
            "121779",
            "121786",
            "268815",
            "268831",
            "272818",
            "273159",
            "275465",
            "403115",
            "403481",
            "403483",
            "403490",
            "403492",
            "403499",
            "403501",
            "403506",
            "121718",
            "121788",
            "403505",
        ]


class MarCleaner(CleanerBase):
    def clean(self, row, row_num=None):
        # only add real addressed into the db, not places
        criteria = {"TYPE_": ["PLACE"]}
        row = self.filter_row_by(row, criteria)
        if not row:  # skip other cleaning steps if filtered out
            return None
        row = self.replace_nulls(row, null_values=["N", "NA", "", None])
        row = self.rename_census_tract(row, column_name="CENSUS_TRACT")
        return row


class ParcelCleaner(CleanerBase):
    def clean(self, row, row_num=None):
        row = self.replace_nulls(row, null_values=["N", "", None, "U"])
        row = self.parse_dates(row)
        return row
