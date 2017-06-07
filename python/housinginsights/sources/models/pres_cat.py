"""
Model for tables from preservation catalog.
"""

PROJ_FIELDS = ['Nlihc_id', 'Status', 'Subsidized', 'Cat_Expiring',
          'Cat_Failing_Insp', 'Proj_Name', 'Proj_City', 'Proj_ST', 'Proj_Zip',
          'Proj_Units_Tot', 'Proj_Units_Assist_Min', 'Proj_Units_Assist_Max',
          'Hud_Own_Effect_dt', 'Hud_Own_Name', 'Hud_Own_Type', 'Hud_Mgr_Name',
          'Hud_Mgr_Type', 'Subsidy_Start_First', 'Subsidy_Start_Last',
          'Subsidy_End_First', 'Subsidy_End_Last', 'Ward2012', 'PBCA',
          'Anc2012', 'Psa2012', 'Geo2010', 'Cluster_tr2000',
          'Cluster_tr2000_name', 'Zip', 'Proj_image_url', 'Proj_streetview_url',
          'Proj_address_id', 'Proj_x', 'Proj_y', 'Proj_lat', 'Proj_lon',
          'Update_Dtm', 'Subsidy_info_source_property', 'contract_number',
          'Proj_addre', 'Bldg_count', 'Category_Code',
          'Cat_At_Risk', 'Cat_More_Info', 'Cat_Lost', 'Cat_Replaced']

ADDRESS_FIELDS = {'lat_lon': ('Proj_lat', 'Proj_lon'),
                  'xy_coords': ('Proj_x', 'Proj_y'),
                  'address': ('Proj_addre', 'Proj_Zip')}

MAR_MAP = {'Proj_Name', 'Proj_City', 'Proj_ST', 'Proj_Zip',
          'Ward2012', 'PBCA',
          'Anc2012', 'Psa2012', 'Cluster_tr2000',
          'Cluster_tr2000_name', 'Zip', 'Proj_image_url', 'Proj_streetview_url',
          'Proj_address_id', 'Proj_x', 'Proj_y', 'Proj_lat', 'Proj_lon',
          'Update_Dtm', 'Subsidy_info_source_property', 'contract_number',
          'Proj_addre', 'Bldg_count', 'Nlihc_id', 'Category_Code',
          'Cat_At_Risk', 'Cat_More_Info', 'Cat_Lost', 'Cat_Replaced'}

SUBSIDY_FIELDS = ['Nlihc_id', 'Subsidy_id',
                      'Units_Assist', 'POA_start', 'POA_end',
                      'contract_number', 'rent_to_fmr_description',
                      'Subsidy_Active', 'Subsidy_Info_Source_ID',
                      'Subsidy_Info_Source', 'Subsidy_Info_Source_Date',
                      'Update_Dtm', 'Program', 'Compl_end', 'POA_end_prev',
                      'Agency', 'POA_start_orig', 'Portfolio',
                      'Subsidy_info_source_property',
                      'POA_end_actual']

