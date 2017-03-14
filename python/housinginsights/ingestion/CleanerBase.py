from abc import ABCMeta, abstractclassmethod, abstractmethod
from datetime import datetime
import dateutil.parser as dateparser

class CleanerBase(object, metaclass=ABCMeta):
    def __init__(self, meta, manifest_row, cleaned_csv='', removed_csv=''):
        self.cleaned_csv = cleaned_csv
        self.removed_csv = removed_csv

        self.manifest_row = manifest_row
        self.tablename = manifest_row['destination_table']
        self.meta = meta
        self.fields = meta[self.tablename]['fields'] #a list of dicts

        self.null_value = 'Null' #what the SQLwriter expects in the temp csv

    def field_meta(self,field):
        for field_meta in self.fields:
            if f['source_name'] == field:
                return field_meta
            return None

    def replace_nulls(self, row, null_values =  ['NA', '-', '+','', None]):
        for key in row:
            if row[key] in null_values:
                row[key] = self.null_value
        return row

    
    def format_date(self, value):
        date = None
        try:
            _date = dateparser.parse(value,dayfirst=False, yearfirst=False)
            #_date = datetime.strptime(value, '%m/%d/%Y')
            date = datetime.strftime(_date, '%Y-%m-%d')
        except Exception as e:
            #TODO add logging w/ full info
            print("Unable to format date properly")
        finally:
            if date is None:
                date = self.null_value
            return date

    def parse_dates(self, row):
        '''
        Tries to automatically parse all dates that are of type:'date' in the meta
        '''
        date_fields = []
        for field in self.fields:
            if field['type'] == 'date':
                date_fields.append(field['source_name'])

        for source_name in date_fields:
            row[source_name] = self.format_date(row[source_name])
        return row

    @abstractmethod
    def clean(self, row, row_num):
        pass


class GenericCleaner(CleanerBase):
    def clean(self,row, row_num = None):
        return row

class BuildingCleaner(CleanerBase):
    def clean(self, row, row_num = None):
        row = self.replace_nulls(row)
        row = self.parse_dates(row)
        return row
    

class ACSRentCleaner(CleanerBase):
    def clean(self,row, row_num = None):
        row = self.high_rent(row)
        row = self.replace_nulls(row)
        if row_num == 0:
            return None
        return row

    def high_rent(self,row):
        '''
        Rent higher than the max reportable value are suppressed
        e.g: instead of being reported as "3752", a plus sign is added
        and the values over the max value are suppressed eg. "3,500+"
        We assume that the actual value is the max value, and strip out the , and +
        '''
        if row['HD01_VD01'][-1] == "+":
            row['HD01_VD01'] = row['HD01_VD01'].replace(',','')
            row['HD01_VD01'] = row['HD01_VD01'].replace('+','')
        return row



#TODO haven't merged this original version w/ latest usage.
class ParcelCleaner(CleanerBase):

    def clean(self, row):
        super(ParcelCleaner, self).replace_nulls(row)
        self.clean_parcel_row(row)

    def clean_parcel_row(self, row):
        if len(row) is not 12:
            print("Print missing columns in row: {}".format(row))
            return 'DIRTY', row

        for k, v in row.items():
            if k == 'Parcel_Info_Source_Date':
                if super(ParcelCleaner, self).format_date(v) == 'N':
                    return 'DIRTY', row
                else:
                    row[k] = super(ParcelCleaner, self).format_date(v)
            if k == 'Parcel_owner_date':
                if super(ParcelCleaner, self).format_date(v) == 'N':
                    return 'DIRTY', row
                else:
                    row[k] = super(ParcelCleaner, self).format_date(v)
        return 'CLEAN', row
