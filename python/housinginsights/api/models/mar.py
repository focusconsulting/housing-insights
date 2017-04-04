"""
Model for mar api.
"""

FIELDS = ['ADDRESS_ID', 'ADDRNUM', 'ADDRNUMSUFFIX', 'ANC', 'ANC_2002',
          'ANC_2012', 'CENSUS_TRACT', 'CITY', 'CLUSTER_', 'ConfidenceLevel',
          'FOCUS_IMPROVEMENT_AREA', 'FULLADDRESS', 'HAS_ALIAS', 'HAS_CONDO_UNIT',
          'HAS_RES_UNIT', 'HAS_SSL', 'IMAGEDIR', 'IMAGENAME', 'IMAGEURL', 'LATITUDE',
          'LONGITUDE', 'MARID', 'NATIONALGRID', 'NBHD_ACTION', 'POLDIST', 'PSA',
          'QUADRANT', 'RES_TYPE', 'ROADWAYSEGID', 'ROC', 'SMD', 'SMD_2002', 'SMD_2012',
          'SSL', 'STATE', 'STATUS', 'STNAME', 'STREETVIEWURL', 'STREET_TYPE',
          'VOTE_PRCNCT', 'WARD', 'WARD_2002', 'WARD_2012', 'XCOORD', 'YCOORD', 'ZIPCODE']


class MarResult(object):
    def __init__(self, result):
        self.data = []
        for attr in FIELDS:
            value = result.get(attr) or ''
            self.data.append(value)
