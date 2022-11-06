"""
Model for affordable housing api
"""

FIELDS = ['OBJECTID', 'MAR_WARD', 'ADDRESS', 'PROJECT_NAME', 'STATUS_PUBLIC',
          'AGENCY_CALCULATED', 'REPORT_UNITS_AFFORDABLE', 'LATITUDE',
          'LONGITUDE', 'ADDRESS_ID', 'XCOORD', 'YCOORD', 'FULLADDRESS',
          'GIS_LAST_MOD_DTTM']

SUBSIDY_FIELDS_MAP = {'Nlihc_id': None, 
                      'Subsidy_id': None,
                      'Units_Assist': 'REPORT_UNITS_AFFORDABLE',
                      'POA_start': None, 
                      'POA_end': None,
                      'contract_number': None, 
                      'rent_to_fmr_description': None,
                      'Subsidy_Active': None, 
                      'Subsidy_Info_Source_ID': None,
                      'Subsidy_Info_Source': None,
                      'Subsidy_Info_Source_Date': None, 
                      'Update_Dtm': None,
                      'Program': 'AGENCY_CALCULATED', 
                      'Compl_end': None, 
                      'POA_end_prev': None,
                      'Agency': None, 
                      'POA_start_orig': None, 
                      'Portfolio': None,
                      'Subsidy_info_source_property': None,
                      'POA_end_actual': None}

PROJECT_FIELDS_MAP = {'Nlihc_id': None,
                      'Status': None, 
                      'Subsidized': None,
                      'Cat_Expiring': None, 
                      'Cat_Failing_Insp': None,
                      'Proj_Name': 'PROJECT_NAME', 
                      'Proj_City': None,
                      'Proj_ST': None, 
                      'Proj_zip': None, 
                      'Proj_Units_Tot': None,
                      'Proj_units_mar': None,
                      'Proj_Units_Assist_Min': "REPORT_UNITS_AFFORDABLE",
                      'Proj_Units_Assist_Max': "REPORT_UNITS_AFFORDABLE",
                      'Hud_Own_Effect_dt': None, 
                      'Hud_Own_Name': None,
                      'Hud_Own_Type': None, 
                      'Hud_Mgr_Name': None,
                      'Hud_Mgr_Type': None, 
                      'Subsidy_Start_First': None,
                      'Subsidy_Start_Last': None, 
                      'Subsidy_End_First': None,
                      'Subsidy_End_Last': None, 
                      'Ward2012': 'MAR_WARD',
                      'Ward2022': 'MAR_WARD',
                      'PBCA': None, 
                      'Anc2012': None, 
                      'Psa2012': None,
                      'Geo2010': None, 
                      'Geo2020': None, 
                      'Cluster_tr2000': None,
                      'Cluster_tr2000_name': None, 
                      'cluster2017': None,
                      'cluster2017_name': None, 
                      'Zip': None,
                      'Proj_image_url': None, 
                      'Proj_streetview_url': None,
                      'Proj_address_id': 'ADDRESS_ID', 
                      'Proj_x': 'XCOORD',
                      'Proj_y': 'YCOORD', 
                      'Proj_lat': 'LATITUDE',
                      'Proj_lon': 'LONGITUDE',
                      'Update_Dtm': 'GIS_LAST_MOD_DTTM',
                      'Subsidy_info_source_property': None,
                      'contract_number': None, 
                      'Proj_addre': 'FULLADDRESS',
                      'Proj_ayb': None,
                      'Proj_eyb': None,
                      'Proj_owner_type':None,
                      'Bldg_count': None, 
                      'Category_Code': None,
                      'Cat_At_Risk': None, 
                      'Cat_More_Info': None,
                      'Cat_Lost': None, 
                      'Cat_Replaced': None
                      }

PROJECT_ADDRE_FIELDS_MAP = {'Nlihc_id': None,
                            'Ssl': None,
                            'Proj_name': 'PROJECT_NAME',
                            'Bldg_zip': None,
                            'Ward2012': 'MAR_WARD',
                            'Anc2012': None,
                            'Psa2012': None,
                            'Geo2010': None,
                            'Cluster_tr2000': None,
                            'Cluster_tr2000_name': None,
                            'Bldg_image_url': None,
                            'Bldg_streetview_url': None,
                            'Bldg_address_id': 'ADDRESS_ID',
                            'Bldg_x': 'XCOORD',
                            'Bldg_y': 'YCOORD',
                            'Bldg_lat': 'LATITUDE',
                            'Bldg_lon': 'LONGITUDE',
                            'Bldg_addre': 'FULLADDRESS'
                            }


class DCHousingResult(object):
    def __init__(self, result):
        self.data = []
        for attr in FIELDS:
            value = result.get(attr) or ''
            self.data.append(value)

