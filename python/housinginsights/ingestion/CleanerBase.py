from abc import ABCMeta, abstractclassmethod, abstractmethod
from datetime import datetime

class CleanerBase(object, metaclass=ABCMeta):
    def __init__(self, meta, manifest_row, cleaned_csv='', removed_csv=''):
        self.cleaned_csv = cleaned_csv
        self.removed_csv = removed_csv

        self.manifest_row = manifest_row
        self.tablename = manifest_row['destination_table']
        self.meta = meta
        self.fields = meta[self.tablename]['fields']

    def field_meta(self,field):
        for field_meta in self.fields:
            if f['source_name'] == field:
                return field_meta
            return None

    @staticmethod
    def replace_nulls(row):
        for key in row:
            if row[key] in ('NA', '-', '+', None):
                row[key] = 'Null'
        return row

    @staticmethod
    def format_date(value):
        date = None
        try:
            _date = datetime.strptime(value, '%m/%d/%Y')
            date = datetime.strftime(_date, '%Y-%m-%d')
        except Exception as e:
            print("Unable to format date properly")
        finally:
            if date is None:
                date = 'Null'
            return date

    @abstractmethod
    def clean(self):
        pass


class GenericCleaner(CleanerBase):
    def clean(self,row):
        return row


class ACSRentCleaner(CleanerBase):
    def clean(self,row):
        row = self.high_rent(row)
        row = self.replace_nulls(row)

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
