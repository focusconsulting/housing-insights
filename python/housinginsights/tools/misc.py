

from housinginsights.sources.mar import MarApiConn
import logging

def quick_address_cleanup(addr):
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
            " St ":" Street ",
            " St. ":" Street ",
            " Pl ":" Place ",
            " Pl. ":" Place ",
            " Ave ":" Avenue ",
            " Ave. ":" Avenue "
        }

        # Format addr by matching the conventions of the MAR
        for key, value in address_string_mapping.items():
            addr = addr.replace(key,value)

        return addr

def check_mar_for_address(addr, conn):
        '''
        Looks for a matching address in the MAR
        Currently just uses a 
        '''

        quick_address_cleanup(addr)

        ###########################
        # Attempt #1 - direct match
        ###########################
        query = """
                select mar_id from mar
                where full_address ='{}'
                """.format(addr.upper())  #MAR uses upper case in the full_address field 

        query_result = conn.execute(query)

        result = [dict(x) for x in query_result.fetchall()]

        if result:
            return result[0]['mar_id']

        ###########################
        # Attempt #2 - MAR API
        ###########################
        logging.info("  checking mar API")
        mar_api = MarApiConn()
        result = mar_api.find_addr_string(address=addr)
        if (result['returnDataset'] == None or 
            result['returnDataset'] == {} or
            result['sourceOperation'] == 'DC Intersection'):

            #Means we didn't find a proper match
            result = None

        if result:
            return result['returnDataset']['Table1'][0]['ADDRESS_ID']

        #If no match found:
        return None



def get_unique_addresses_from_str(address_str=""):

    def _trim_str(add_str):
        """Helper function that does some simple string cleaning."""
        add_str = add_str.lstrip()
        add_str = add_str.rstrip()
        return add_str

    def _parse_semicolon_delimiter(address_list):
        """Helper function that handles parsing semicolon delimiters"""
        output = list()
        for add_str in address_list:
            temp_results = add_str.split(sep=';')
            if len(temp_results) > 1:
                for address in temp_results:
                    output.append(_trim_str(address))
            else:
                output.append(add_str)
        return output

    def _parse_and_delimiter(address_list):
        """Helper function that handles parsing 'and' delimiters"""
        output = list()
        for add_str in address_list:
            temp_results = add_str.split(sep=' and ')
            if len(temp_results) > 1:
                for address in temp_results:
                    output.append(_trim_str(address))
            else:
                output.append(add_str)
        return output

    def _parse_ampersand_delimiter(address_list):
        """Helper function that handles parsing '&' delimiters"""
        output = list()
        for add_str in address_list:
            temp_results = add_str.split(sep='&')
            if len(temp_results) > 1:
                num_1 = _trim_str(temp_results[0])
                base = _trim_str(temp_results[1])
                num_2, base = base.split(' ', 1)
                num_2 = _trim_str(num_2)
                base = _trim_str(base)

                output.append('{} {}'.format(num_1, base))
                output.append('{} {}'.format(num_2, base))
            else:
                output.append(add_str)
        return output

    def _parse_dash_delimiter(address_list):
        """Helper function that handles parsing '-' delimiters"""
        output = list()
        for add_str in address_list:
            temp_results = add_str.split(sep='-')
            if len(temp_results) > 1:
                num_1 = _trim_str(temp_results[0])
                base = _trim_str(temp_results[1])
                num_2, base = base.split(' ', 1)
                num_2 = _trim_str(num_2)
                base = _trim_str(base)

                #TODO is this properly handling a bad address range situation??
                if not isinstance(num_1,int) or not isinstance(num_2,int):
                    #there was some parseing problem - throw it back
                    output.append(add_str)
                    continue

                # check whether odd, even, or ambiguous range
                even = True if int(num_1) % 2 == 0 else False

                if (int(num_2) % 2 == 0 and not even) or (
                            int(num_2) % 2 != 0 and even):
                    even = None

                # populate address number ranges
                step = 1 if even is None else 2
                for num in range(int(num_1), int(num_2) + 1, step):
                    output.append('{} {}'.format(num, base))
            else:
                output.append(add_str)
        return output

    result = [address_str]  # tracks unique addresses from address_str

    # 1: parse complete address delimiters - ';', 'and'
    result = _parse_semicolon_delimiter(result)
    result = _parse_and_delimiter(result)

    # 2: parse address number range delimiters  - '&', '-'
    result = _parse_ampersand_delimiter(result)
    result = _parse_dash_delimiter(result)

    return result