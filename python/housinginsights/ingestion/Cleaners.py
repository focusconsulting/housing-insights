from abc import ABCMeta, abstractclassmethod, abstractmethod
from datetime import datetime
import dateutil.parser as dateparser
import logging

'''
Usage:
Dynamically import based on name of class in meta.json:
http://stackoverflow.com/questions/4821104/python-dynamic-instantiation-from-string-name-of-a-class-in-dynamically-imported
'''
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
    def remove_line_breaks(self,row):
        #TODO see if it's possible to not do this by getting the copy_from to be ok with breaks
        for key in row:
            row[key] = row[key].replace('\r','__')
            row[key] = row[key].replace('\n','__')
        return row
    
    def format_date(self, value):
        date = None
        try:
            _date = dateparser.parse(value,dayfirst=False, yearfirst=False)
            #_date = datetime.strptime(value, '%m/%d/%Y')
            date = datetime.strftime(_date, '%Y-%m-%d')
        except Exception as e:
            if value is None or value == self.null_value:
                date = self.null_value
            else:
                logging.warning("Unable to format date properly: {}".format(value))
                date=self.null_value

        return date

    def convert_boolean(self,value):
        mapping = {
            'Yes':True,
            'No':False,
            'Y': True,
            'N':False,
            'TRUE':True,
            'FALSE':False,
            '1':True,
            '0':False
            }
        return mapping[value]

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

#############################################
# Custom Cleaners
#############################################

class GenericCleaner(CleanerBase):
    def clean(self,row, row_num = None):
        return row

class ProjectCleaner(CleanerBase):
    def clean(self, row, row_num = None):
        row = self.replace_nulls(row, null_values=['N','', None])
        row = self.parse_dates(row)
        return row

class SubsidyCleaner(CleanerBase):
    def clean(self, row, row_nume=None):
        row['Subsidy_Active'] = self.convert_boolean(row['Subsidy_Active'])
        row['POA_end_actual'] = self.null_value if row['POA_end_actual']=='U' else row['POA_end_actual']
        row = self.replace_nulls(row, null_values = ['N','',None])
        row = self.parse_dates(row)
        return row

class BuildingPermitsCleaner(CleanerBase):
    def clean(self, row, row_num = None):

        row = self.replace_nulls(row, null_values=['NONE','', None])
        row = self.parse_dates(row)
        row = self.remove_line_breaks(row)

        return row

class ACSRentCleaner(CleanerBase):
    def clean(self,row, row_num = None):
        row = self.high_low_rent(row)
        #Note, we are losing data about statistical issues. Would be better to copy these to a new column.
        row = self.replace_nulls(row,null_values=['N','**','***','****','*****','(X)','-',''])
        if row_num == 0:
            return None
        return row

    def high_low_rent(self,row):
        '''
        Rent higher than the max reportable value are suppressed
        e.g: instead of being reported as "3752", a plus sign is added
        and the values over the max value are suppressed eg. "3,500+"
        Rent lower than the lowest reportable is similar (e.g. "100-")
        We assume that the actual value is the max value, and strip out the , and +
        '''
        if row['HD01_VD01'][-1] == "+":
            row['HD01_VD01'] = row['HD01_VD01'].replace(',','')
            row['HD01_VD01'] = row['HD01_VD01'].replace('+','')
        if row['HD01_VD01'][-1] == "-":
            row['HD01_VD01'] = row['HD01_VD01'].replace(',','')
            row['HD01_VD01'] = row['HD01_VD01'].replace('-','')
        return row


