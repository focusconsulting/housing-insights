"""
Model for affordable housing api
"""

FIELDS = ['OBJECTID', 'MAR_WARD', 'ADDRESS', 'PROJECT_NAME', 'STATUS_PUBLIC',
          'AGENCY_CALCULATED', 'REPORT_UNITS_AFFORDABLE', 'LATITUDE',
          'LONGITUDE', 'ADDRESS_ID', 'XCOORD', 'YCOORD', 'FULLADDRESS',
          'GIS_LAST_MOD_DTTM']


class HousingResult(object):
    def __init__(self, result):
        self.data = []
        for attr in FIELDS:
            value = result.get(attr) or ''
            self.data.append(value)

