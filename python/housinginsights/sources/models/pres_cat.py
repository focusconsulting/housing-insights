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

CLUSTER_DESC_MAP = {
    'Cluster 1': 'Kalorama Heights, Adams Morgan, Lanier Heights',
    'Cluster 2': 'Columbia Heights, Mt. Pleasant, Pleasant Plains, Park View',
    'Cluster 3': 'Howard University, Le Droit Park, Cardozo/Shaw',
    'Cluster 4': 'Georgetown, Burleith/Hillandale',
    'Cluster 5': 'West End, Foggy Bottom, GWU',
    'Cluster 6': 'Dupont Circle, Connecticut Avenue/K Street',
    'Cluster 7': 'Shaw, Logan Circle',
    'Cluster 8': 'Downtown, Chinatown, Penn Quarters, Mount Vernon Square,'
    'North Capitol Street',
    'Cluster 9': 'Southwest Employment Area, Southwest/Waterfront, Fort McNair,'
    'Buzzard Point',
    'Cluster 10': 'Hawthorne, Barnaby Woods, Chevy Chase',
    'Cluster 11': 'Friendship Heights, American University Park, Tenleytown',
    'Cluster 12': 'North Cleveland Park, Forest Hills, Van Ness',
    'Cluster 13': 'Spring Valley, Palisades, Wesley Heights, Foxhall Crescent,'
                  'Foxhall Village, Georgetown Reservoir',
    'Cluster 14': 'Cathedral Heights, McLean Gardens, Glover Park',
    'Cluster 15': 'Cleveland Park, Woodley Park, Massachusetts Avenue Heights,'
                  'Woodland-Normanstone Terrace',
    'Cluster 16': 'Colonial Village, Shepherd Park, North Portal Estates',
    'Cluster 17': 'Takoma, Brightwood, Manor Park',
    'Cluster 18': 'Brightwood Park, Crestwood, Petworth',
    'Cluster 19': 'Lamond Riggs, Queens Chapel, Fort Totten, Pleasant Hill',
    'Cluster 20': 'North Michigan Park, Michigan Park, University Heights',
    'Cluster 21': 'Edgewood, Bloomingdale, Truxton Circle, Eckington',
    'Cluster 22': 'Brookland, Brentwood, Langdon',
    'Cluster 23': 'Ivy City, Arboretum, Trinidad, Carver Langston',
    'Cluster 24': 'Woodridge, Fort Lincoln, Gateway',
    'Cluster 25': 'NoMa, Union Station, Stanton Park, Kingman Park',
    'Cluster 26': 'Capitol Hill, Lincoln Park',
    'Cluster 27': 'Near Southeast, Navy Yard',
    'Cluster 28': 'Historic Anacostia',
    'Cluster 29': 'Eastland Gardens, Kenilworth',
    'Cluster 30': 'Mayfair, Hillbrook, Mahaning Heights',
    'Cluster 31': 'Deanwood, Burrville, Grant Park, Lincoln Heights,'
                  'Fairmont Heights',
    'Cluster 32': 'River Terrace, Benning, Greenway, Fort Dupont',
    'Cluster 33': 'Capitol View, Marshall Heights, Benning Heights',
    'Cluster 34': 'Twining, Fairlawn, Randle Highlands, Penn Branch,'
                  'Fort Davis Park, Dupont Park',
    'Cluster 35': 'Fairfax Village, Naylor Gardens, Hillcrest, Summit Park',
    'Cluster 36': 'Woodland/Fort Stanton, Garfield Heights, Knox Hill',
    'Cluster 37': 'Sheridan, Barry Farm, Buena Vista',
    'Cluster 38': 'Douglass, Shipley Terrace',
    'Cluster 39': 'Congress Heights, Bellevue, Washington Highlands'
}

