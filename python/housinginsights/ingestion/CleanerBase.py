from abc import ABCMeta, abstractclassmethod, abstractmethod
from datetime import datetime

class CleanerBase(object, metaclass=ABCMeta):
    def __init__(self, meta, cleaned_csv='', removed_csv=''):
        self.meta = meta
        self.cleaned_csv = cleaned_csv
        self.removed_csv = removed_csv

    @staticmethod
    def replace_nulls(row):
        for idx, value in enumerate(row):
            if value in ('NA', '-', '+', None):
                row[idx] = 'Null'

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