from housinginsights.sources.mar import MarApiConn

from housinginsights.tools.logger import HILogger

logger = HILogger(name=__file__, logfile="sources.log")


def quick_address_cleanup(addr):
    # Used to perform common string replacements in addresses.
    # The key is original, value is what we want it to become
    # values match format typically found in the mar table
    # Allows first-pass matching of address strings to the MAR
    # (failed matches are then bumped up to more robust methods)
    address_string_mapping = {
        "Northeast": "NE",
        "Northwest": "NW",
        "Southeast": "SE",
        "Southwest": "SW",
        " St ": " Street ",
        " St. ": " Street ",
        " Pl ": " Place ",
        " Pl. ": " Place ",
        " Ave ": " Avenue ",
        " Ave. ": " Avenue ",
        "N.E.": "NE",
        "N.W.": "NW",
        "S.E.": "SE",
        "S.W.": "SW",
    }

    # Format addr by matching the conventions of the MAR
    for key, value in address_string_mapping.items():
        addr = addr.replace(key, value)

    return addr


def check_mar_for_address(addr, conn):
    """
    Looks for a matching address in the MAR
    Currently just uses a
    """

    quick_address_cleanup(addr)

    ###########################
    # Attempt #1 - direct match
    ###########################
    query = """
                select mar_id from mar
                where full_address ='{}'
                """.format(
        addr.upper()
    )  # MAR uses upper case in the full_address field

    query_result = conn.execute(query)

    result = [dict(x) for x in query_result.fetchall()]

    if result:
        return result[0]["mar_id"]

    ###########################
    # Attempt #2 - MAR API
    ###########################
    logger.info("  checking mar API")
    mar_api = MarApiConn()
    result = mar_api.find_addr_string(address=addr)
    if (
        result["returnDataset"] is None
        or result["returnDataset"] == {}
        or result["sourceOperation"] == "DC Intersection"
    ):

        # means we didn't find a proper match
        result = None

    # make sure to return address id as string and not default integer
    if result:
        return str(result["returnDataset"]["Table1"][0]["ADDRESS_ID"])

    # if no match found:
    return None


def get_unique_addresses_from_str(address_string=""):
    """
    Utility method for parsing an address string into a list of well
    formatted unique addresses: "<address number> <street name> <quadrant>". The
    process involves first parsing multiple address delimiters (semicolons and
    " and ") into a list. Then for each result parsing address number range
    delimiters to get a list of unique addresses.

    :param address_string: the address string to be processed
    :return: a list of unique addresses
    """

    # Helper functions for multiple address delimiters parsing #
    def _parse_semicolon_delimiter(address_list):
        """Helper function that handles parsing semicolon delimiters"""
        output = list()
        for add_str in address_list:
            temp_results = add_str.split(sep=";")
            if len(temp_results) > 1:
                for address in temp_results:
                    output.append(address.strip())
            else:
                output.append(add_str)
        return output

    def _parse_and_delimiter(address_list):
        """Helper function that handles parsing 'and' delimiters"""
        output = list()
        for add_str in address_list:
            temp_results = add_str.split(sep=" and ")
            if len(temp_results) > 1:
                for address in temp_results:
                    output.append(address.strip())
            else:
                output.append(add_str)
        return output

    logger.info("Parsing address: {}".format(address_string))
    # Begin parsing process #
    # used to track resulting addresses from multiple address delimiter parsing
    multiple_addresses_result = [address_string]

    # 1: first parse multiple address delimiters: ';', 'and'
    multiple_addresses_result = _parse_semicolon_delimiter(multiple_addresses_result)
    multiple_addresses_result = _parse_and_delimiter(multiple_addresses_result)

    # 2: second parse address numbers delimiters #
    unique_addresses_result = list()

    # iterate through results from parsing multiple address delimiters
    for addr_str in multiple_addresses_result:
        logger.info("Parsing string portion '{}'".format(addr_str))
        if len(addr_str) > 0:
            # handle 'other's special case
            if addr_str == "others":
                unique_addresses_result.append(addr_str)
                continue

            delimiter_stack = list()  # used to track delimiters within addr_str
            str_stack = list()  # used to track string literals in addr_str

            # populate delimiter_stack and str_stack accordingly from addr_str
            _str = ""
            for char in addr_str:
                if char in {"-", ",", "&"}:
                    if len(_str) > 0:  # add current str partition into stack
                        str_stack.append(_str)
                        _str = ""  # restart str tracking
                    delimiter_stack.append(char)
                else:
                    _str += char

            # validate stacks to handle contiguous range delimiter cases
            if len(delimiter_stack) > len(str_stack):
                logger.warning("Invalid address: {}".format(addr_str))
                unique_addresses_result.append(addr_str)
                continue

            base_str = _str.strip()  # initialize base to be remaining _str val

            # Determine 'address_num' and '<streetname> <quadrant' base for
            # generating all unique addresses for addr_str. If it cannot be
            # partitioned accordingly return addr_str as-is
            try:
                addr_num, base = base_str.split(" ", 1)
                _ = int(addr_num)  # validate address number partition
                unique_addresses_result.append(base_str)
            except ValueError:
                # handle '<streetname>, <quadrant>' address cases
                try:
                    delim = delimiter_stack.pop()
                except:
                    # this will trigger the invalid address 'else' statement
                    delim = ""

                if delim == ",":
                    _str = str_stack.pop().strip()

                    # flag '<address_num>, <streetname> <quadrant>' as invalid case
                    try:
                        _ = int(_str)
                        logger.warning("Invalid address: {}".format(addr_str))
                        unique_addresses_result.append(addr_str)
                        continue
                    except ValueError:
                        base_str = "{} {}".format(_str, base_str)
                        addr_num, base = base_str.split(" ", 1)
                        unique_addresses_result.append(base_str)

                else:  # fail cleanly for all other invalid cases
                    logger.warning("Invalid address: {}".format(addr_str))
                    unique_addresses_result.append(addr_str)
                    continue

            num = addr_num  # reset prior to parsing new 'addr_str' batch

            while delimiter_stack:
                # get next delimiter
                delim = delimiter_stack.pop()

                if delim == ",":
                    num = str_stack.pop().strip()
                    unique_addresses_result.append("{} {}".format(num, base))

                elif delim == "-":
                    shift_range_by = 0  # exclude original base address number?
                    # handle composites - check num exists and assign accordingly
                    try:
                        addr_num = num
                        num = str_stack.pop().strip()
                    except NameError as e:
                        logger.warning(
                            'Missing "num" - using default addr_num: {}'.format(e)
                        )
                        num = str_stack.pop().strip()

                    # check range style and convert accordingly 1210-12 vs 1210-1212
                    if len(num) > len(addr_num):
                        diff = len(num) - len(addr_num)
                        addr_num = num[:diff] + addr_num
                        # remove added based_str in final_pass_result and shift range by 1
                        _ = unique_addresses_result.pop()
                        shift_range_by += 1

                    # check whether odd, even, or ambiguous range
                    even = True if int(num) % 2 == 0 else False

                    if (int(addr_num) % 2 == 0 and not even) or (
                        int(addr_num) % 2 != 0 and even
                    ):
                        even = None

                    # populate address number ranges
                    step = 1 if even is None else 2

                    for cur_num in range(
                        int(num), int(addr_num) + shift_range_by, step
                    ):
                        unique_addresses_result.append("{} {}".format(cur_num, base))

                elif delim == "&":
                    num = str_stack.pop().strip()

                    if num == "":  # skip if next in str is empty or space
                        continue

                    try:
                        # check if actually number, else return original
                        _ = int(num)
                        unique_addresses_result.append("{} {}".format(num, base))
                    except ValueError:
                        # remove previous result that was added incorrectly
                        _ = unique_addresses_result.pop()
                        logger.warning("Invalid address: {} & {}".format(num, base_str))
                        unique_addresses_result.append("{} & {}".format(num, base_str))

    return unique_addresses_result
