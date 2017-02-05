from datetime import datetime


class Cleaner(object):
    """
    A cleaner object for csv files
    """
    def __init__(self):
        self.TYPES = {
            'parcel': self.clean_parcel_row
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

    def clean_parcel_row(self, row):
        # There should be twelve keys
        if len(row) is not 12:
            print("Missing column(s) in row: {}".format(row))
            return 'DIRTY', row

        # Iterate through each column
        for k, v in row.iteritems():
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


def format_date(date_string):
    if date_string == 'N':
        return 'N'
    else:
        _date = datetime.strptime(date_string, '%m/%d/%Y')
        return datetime.strftime(_date, '%Y-%m-%d')


def trim_whitespace(value):
    return value.strip()