from datetime import datetime


class Cleaner(object):
    """
    A cleaner object for csv files
    """
    def __init__(self):
        self.TYPES = {
            'parcel': self.clean_parcel_row,
            'reac_score': self.clean_reac_score_row
        }

    def clean(self, _type, row):
        """
        Reads type and determines which function to use to clean the row based on type
        :param _type: type of cleaning function that should be used.
        :param row: Row that is being cleaned.
        :return:
        """
        _func = self.TYPES[_type]
        return _func(row)

    # TODO need to come up with heuristics to clean different csv files.
    def clean_parcel_row(self, row):
        # There should be twelve keys
        if len(row) is not 12:
            print("Missing column(s) in row: {}".format(row))
            return 'DIRTY', row

        # Iterate through each column
        for k, v in row.items():
            # Format Dates to ISO 8601 standards...
            if k == 'Parcel_Info_Source_Date':
                if format_date(row['Parcel_Info_Source_Date']) == 'N':
                    return 'DIRTY', row
                else:
                    row['Parcel_Info_Source_Date'] = format_date(row['Parcel_Info_Source_Date'])
            if k == 'Parcel_owner_date':
                if format_date(row['Parcel_owner_date']) == 'N':
                    return 'DIRTY', row
                else:
                    row['Parcel_owner_date'] = format_date(row['Parcel_owner_date'])

            # Format parcel owners if there are more than one into a comma separated list.
            if '+' in row['Parcel_owner_name']:
                row['Parcel_owner_name'] = row['Parcel_owner_name'].replace(' +', ',')

            # TODO Will need more heuristics on what we expect we will encounter and will need to be cleaned.
        return 'CLEAN', row

    def clean_reac_score_row(self, row):
        if len(row) is not 6:
            print("Missing column(s) in row: {}".format(row))
            return 'DIRTY', row
        for k, v in row.iteritems():
            row[k] = trim_whitespace(v)
            if k == 'REAC_date':
                if format_date(row['REAC_date']) == 'N':
                    return 'DIRTY', row
                else:
                    row['REAC_date'] = format_date(row['REAC_date'])
        return 'CLEAN', row


def format_date(date_string):
    if date_string == 'N':
        return 'N'
    else:
        _date = datetime.strptime(date_string, '%m/%d/%Y')
        return datetime.strftime(_date, '%Y-%m-%d')


def trim_whitespace(value):
    return value.strip()






#############################
# This stuff copied over from DataWriter. This functionality should be integrated into the Cleaner object itself, instead of requiring a separate object to be instantiated. 
# That way, Cleaner just knows how to write its cleaned data to a file

class OldDataWriter(object):
    """
    Class that will handle writing out the clean and dirty csv files
    """
    def __init__(self, clean_file, dirty_file, fieldnames):
        _root = os.getcwd()
        self._clean_file = open(os.path.join(_root, clean_file), 'w')
        self._dirty_file = open(os.path.join(_root, dirty_file), 'w')

        self._clean_writer = DictWriter(self._clean_file, fieldnames=fieldnames)
        self._dirty_writer = DictWriter(self._dirty_file, fieldnames=fieldnames)

        # Write the header for both files
        self._clean_writer.writeheader()
        self._dirty_writer.writeheader()

    def write_row(self, row, disposition):
        """
        Write a row to csv file
        :param row: dictionary row to be written
        :param disposition which csv file to write to
        """
        if disposition == 'CLEAN':
            self._clean_writer.writerow(row)
        elif disposition == 'DIRTY':
            self._dirty_writer.writerow(row)
        else:
            print("Can't determine disposition of row")

    def save(self):
        self._clean_file.close()
        self._dirty_file.close()