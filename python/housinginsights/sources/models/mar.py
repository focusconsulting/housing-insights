"""
Model for mar api.
"""

FIELDS = [
    "ADDRESS_ID",
    "ADDRNUM",
    "ADDRNUMSUFFIX",
    "ANC",
    "ANC_2002",
    "ANC_2012",
    "CENSUS_TRACT",
    "CITY",
    "CLUSTER_",
    "ConfidenceLevel",
    "FOCUS_IMPROVEMENT_AREA",
    "FULLADDRESS",
    "HAS_ALIAS",
    "HAS_CONDO_UNIT",
    "HAS_RES_UNIT",
    "HAS_SSL",
    "IMAGEDIR",
    "IMAGENAME",
    "IMAGEURL",
    "LATITUDE",
    "LONGITUDE",
    "MARID",
    "NATIONALGRID",
    "NBHD_ACTION",
    "POLDIST",
    "PSA",
    "QUADRANT",
    "RES_TYPE",
    "ROADWAYSEGID",
    "ROC",
    "SMD",
    "SMD_2002",
    "SMD_2012",
    "SSL",
    "STATE",
    "STATUS",
    "STNAME",
    "STREETVIEWURL",
    "STREET_TYPE",
    "VOTE_PRCNCT",
    "WARD",
    "WARD_2002",
    "WARD_2012",
    "XCOORD",
    "YCOORD",
    "ZIPCODE",
]

CONDO_FIELDS = ["UNITNUM", "UNITTYPE", "UNITSSL", "STATUS", "MARID", "ADDRESS_ID"]

MAR_TO_TABLE_FIELDS = {
    "ADDRNUM": "address_number",
    "ADDRNUMSUFFIX": "address_number_suffix",
    "ANC": "anc",
    "CENSUS_TRACT": "census_tract",
    "CITY": "city",
    "CLUSTER_": "neighborhood_cluster",
    "FOCUS_IMPROVEMENT_AREA": "focus_improvement_area",
    "FULLADDRESS": "full_address",
    "LATITUDE": "latitude",
    "LONGITUDE": "longitude",
    "MARID": "mar_id",
    "NATIONALGRID": "national_grid",
    "POLDIST": "poldist",
    "PSA": "psa",
    "QUADRANT": "quadrant",
    "RES_TYPE": "res_type",
    "ROC": "roc",
    "SMD": "smd",
    "SMD_2002": "smd_2002",
    "SMD_2012": "smd_2012",
    "SSL": "ssl",
    "STATE": "state",
    "STATUS": "status",
    "STNAME": "street_name",
    "STREET_TYPE": "street_type",
    "VOTE_PRCNCT": "vote_precinct",
    "WARD": "ward",
    "WARD_2002": "ward_2002",
    "WARD_2012": "ward_2012",
    "XCOORD": "xcoord",
    "YCOORD": "ycoord",
    "ZIPCODE": "zipcood",
}


class MarResult(object):
    def __init__(self, result):
        self.data = []
        for attr in FIELDS:
            value = result.get(attr) or ""
            self.data.append(value)


class CondoResult(object):
    def __init__(self, result):
        self.data = []
        for attr in CONDO_FIELDS:
            value = result.get(attr) or ""
            self.data.append(value)
