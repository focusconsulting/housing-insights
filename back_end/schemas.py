'''
schemas.py
----------

This file allows us to select what columns we want from database models, and
save them as json output.
'''
from new_app import ma
#import models

class TestSchema(ma.Schema):
    class Meta:
        # Fields to expose
        #model = models.NewProject
        fields = ('nlihc_id', 'latitude', 'longitude' )

