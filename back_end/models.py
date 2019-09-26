'''
This file contains models to send data from the database to the front end via
the API. Rather than use automap or reflections, we are explicit about what
we are putting in the project and subsidy tables.

The tables are:
    - Project (Updated with Preservation Catalog)
    - Subsidy (Updated with Preservation Catalog)
    - Crime (Updated Daily)
    - Permit (Updated Daily)
    - Acs (Updated with ACS 5 year estimates)
'''
from app import db

class NewProject(db.Model):
    '''
    Each observation in the project table is a single housing project and
    is identified with the nlihc_id. Projects that came from Open Data DC
    were given a string ID in this same column.

    When called by "api/project", this table provides:
      - nlihc_id
      - latitude
      - longitude
      - proj_name
      - proj_addre
      - ward
      - proj_units_assist_max
      - proj_units_tot
      - neighborhood_cluster_desc

    When called by "api/filter", this table provides all of the attributes
    below except longitude and latitude.
    '''
    __tablename__ = 'new_project'
    #__table_args__ = {'extend_existing': True}

    # Identificaton and Geography 
    nlihc_id = db.Column(db.String, primary_key=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    census_tract = db.Column(db.String, nullable=False)
    neighborhood_cluster = db.Column(db.String, nullable=False)
    ward = db.Column(db.String, nullable=False)
    #neighborhood_cluster_desc = db.Column(db.String)

    ## Basic Project Information
    proj_name = db.Column(db.String, nullable=False)
    proj_addre = db.Column(db.String, nullable=False)
    proj_units_tot = db.Column(db.Integer)
    proj_units_assist_max = db.Column(db.Integer)
    proj_owner_type = db.Column(db.String)

    # Extended Project Information
    #most_recent_topa_date = db.Column(db.DateTime)
    #topa_count = db.Column(db.Integer)
    most_recent_reac_score_num = db.Column(db.Integer)
    most_recent_reac_score_date = db.Column(db.DateTime)
    sum_appraised_value_current_total = db.Column(db.Float)

    ## One to many relationship with subsidy.
    subsidy = db.relationship('NewSubsidy', backref='new_project', lazy=True)

    def __repr__(self):
        '''A string representation for testing.'''
        return 'PROJECT {}: ({}, {})'.format(
                self.nlihc_id, self.latitude, self.longitude
                )


class NewSubsidy(db.Model):
    '''
    Each observation in the subsidy table is a single subsidy, which may be one
    of many for a single housing project. It is also identified with the nlihc_id.

    When called by "api/filter", this table provides all of the attributes
    below.

    These could be added to the project table, but for now this table is
    separate incase more subsidy information is needed later.
    '''
    __tablename__ = 'new_subsidy'

    subsidy_id = db.Column(db.Integer, primary_key=True)
    nlihc_id = db.Column(db.String, db.ForeignKey('new_project.nlihc_id'))
    portfolio = db.Column(db.String)
    poa_start = db.Column(db.DateTime)
    poa_end = db.Column(db.DateTime)

    def __repr__(self):
        return 'Subsidy {} for project: {}'.format(self.subsidy_id, self.nlihc_id)
