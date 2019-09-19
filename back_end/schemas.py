'''
schemas.py
----------

This file allows us to select what columns we want from database models, and
save them as json output.
'''
from new_app import ma
#import models

class NewProjectSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('nlihc_id',
                'latitude',
                'longitude',
               'census_tract',
               'neighborhood_cluster',
               'ward',
               #'neighborhood_cluster_desc',
                ## Basic Project Information
               'proj_name',
               'proj_addre',
               'proj_units_tot',
               'proj_units_assist_max',
               'proj_owner_type',
        )

new_project_schema = NewProjectSchema(many=True)

class NewFilterSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('nlihc_id',
                  #'subsidy'
                  #'subsidy.portfolio',
                  #'subsidy.poa_start',
                  #'subsidy.poa_end'
                  )
new_filter_schema = NewFilterSchema(many=True)

