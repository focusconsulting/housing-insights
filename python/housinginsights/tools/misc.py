

from housinginsights.sources.mar import MarApiConn
import logging

def check_mar_for_address(addr, conn):
        '''
        Looks for a matching address in the MAR
        Currently just uses a 
        '''

        #Used to perform common string replacements in addresses. 
        #The key is original, value is what we want it to become
        #values match format typically found in the mar table
        #Allows first-pass matching of address strings to the MAR
            # (failed matches are then bumped up to more robust methods)
        address_string_mapping = {
            "Northeast":"NE",
            "Northwest":"NW",
            "Southeast":"SE",
            "Southwest":"SW",
            "St ":"Street ",
            "St. ":"Street ",
            "Pl ":"Place ",
            "Pl. ":"Place ",
            "Ave ":"Avenue ",
            "Ave. ":"Avenue "
        }

        # Format addr by matching the conventions of the MAR
        for key, value in address_string_mapping.items():
            addr = addr.replace(key,value)

        ###########################
        # Attempt #1 - direct match
        ###########################
        query = """
                select mar_id from mar
                where full_address ='{}'
                """.format(addr.upper()) #MAR uses upper case in the full_address field

        query_result = conn.execute(query)

        result = [dict(x) for x in query_result.fetchall()]

        if result:
            return result[0]['mar_id']

        ###########################
        # Attempt #2 - MAR API
        ###########################
        logging.info("  checking mar API")
        mar_api = MarApiConn()
        result = mar_api.find_location(location=addr)
        if (result['returnDataset'] == None or 
            result['returnDataset'] == {} or
            result['sourceOperation'] == 'DC Intersection'):

            #Means we didn't find a proper match
            result = None

        if result:
            return result['returnDataset']['Table1'][0]['ADDRESS_ID']

        #If no match found:
        return None