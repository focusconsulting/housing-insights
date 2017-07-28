# -*- coding: utf-8 -*-

"""
flask api
~~~~~~~~~
This is a simple Flask applicationlication that creates SQL query endpoints.


TODO, as of 6/15/2017 none of these endpoints are SQL Injection ready

"""

from flask import Flask, request, Response, abort, json

import psycopg2
from sqlalchemy import create_engine

import logging
from flask_cors import CORS, cross_origin

import math
import sys

#Different json output methods.
# Currently looks like best pick is jsonify, but with the simplejson package pip-installed so that
# jsonify will uitilize simplejson's decimal conversion ability.
import json
import simplejson
from flask import jsonify
from flask.json import JSONEncoder
import calendar
from datetime import datetime, date
import dateutil.parser as dateparser
from flask_sqlalchemy import SQLAlchemy
from flask_restless import APIManager
from sqlalchemy import MetaData
from sqlalchemy.ext.automap import automap_base


#######################
# Setup
#######################
logging.basicConfig(level=logging.DEBUG)
application = Flask(__name__)


#######################
# Flask Restless Setup
#######################
with open('housinginsights/secrets.json') as f:
    secrets = json.load(f)
    connect_str = secrets['docker_database']['connect_str']

application.config['SQLALCHEMY_DATABASE_URI'] = connect_str
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(application)
Base = automap_base()

metadata = MetaData(bind=db)

Base.prepare(db.engine, reflect=True)

db.session.commit()

BuildingPermits = Base.classes.building_permits
Census = Base.classes.census
# This table is not importing correctly
# CensusMarginOfError = Base.classes.census_margin_of_error
Crime = Base.classes.crime
DcTax = Base.classes.dc_tax
Project = Base.classes.project
ReacScore = Base.classes.reac_score
RealProperty = Base.classes.real_property
Subsidy = Base.classes.subsidy
Topa = Base.classes.topa
WmataDist = Base.classes.wmata_dist
WmataInfo = Base.classes.wmata_info

models = [BuildingPermits, Census, Crime, DcTax, Project, ReacScore,
          RealProperty, Subsidy, Topa, WmataDist, WmataInfo
          ]

manager = APIManager(application, flask_sqlalchemy_db=db)


class CustomJSONEncoder(JSONEncoder):
# uses datetime override http://flask.pocoo.org/snippets/119/
    def default(self, obj):
        try:
            if isinstance(obj,date):
                return datetime.strftime(obj,'%Y-%m-%d')
            if isinstance(obj, datetime):
                return datetime.strftime(obj,'%Y-%m-%d')
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

# apply the custom encoder to the app. All jsonify calls will use this method
application.json_encoder = CustomJSONEncoder


# Allow cross-origin requests. TODO should eventually lock down the permissions on this a bit more strictly, though only allowing GET requests is a good start.
CORS(application, resources={r"/api/*": {"origins": "*"}}, methods=['GET'])

# Allow us to test locally if desired
if 'docker' in sys.argv:
    database_choice = 'docker_database'
else:
    database_choice = 'remote_database'

with open('housinginsights/secrets.json') as f:
    secrets = json.load(f)
    connect_str = secrets[database_choice]['connect_str']


# Should create a new connection each time a separate query is needed so that API can recover from bad queries
# Engine is used to create connections in the below methods
engine = create_engine(connect_str)

# Establish a list of tables so that we can validate queries before executing
conn = engine.connect()
q = "SELECT tablename FROM pg_catalog.pg_tables where schemaname = 'public'"
proxy = conn.execute(q)
results = proxy.fetchall()
tables = [x[0] for x in results]
application.logger.debug('Tables available: {}'.format(tables))
conn.close()
logging.info(tables)

##########################################
# API Endpoints
##########################################

#######################
# Test endpoints - prove things work

# Is the application running?
@application.route('/')
def hello():
    return("The Housing Insights API Rules!")

# Can we access the housinginsights package folder?
import housinginsights.tools.test_util as test_util
@application.route('/housinginsights')
def test_housinginsights_package():
    return(test_util.api_demo_variable)


 # an we make blueprints with passed in arguments?
from api.demo_blueprint_constructor import construct_demo_blueprint
created_blueprint = construct_demo_blueprint("This is my choice")
application.register_blueprint(created_blueprint)

# What urls are available (NOTE must have default params)?
from flask import url_for
def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@application.route("/site-map")
def site_map():
    links = []
    for rule in application.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
    return str(links)

#######################
#Register blueprints
#######################

from api.summarize_observations import construct_summarize_observations
from api.project_view_blueprint import construct_project_view_blueprint
from api.filter_blueprint import construct_filter_blueprint
from api.zone_facts_blueprint import construct_zone_facts_blueprint

# Generate blueprints w/ any needed arguments
sum_obs_blue = construct_summarize_observations('sum_obs',engine)
project_view_blue = construct_project_view_blueprint('project_view',engine)
filter_blue = construct_filter_blueprint('filter', engine)
zone_facts = construct_zone_facts_blueprint('zone_facts',engine)

# Register all the blueprints
for blueprint in [sum_obs_blue, project_view_blue, filter_blue, zone_facts]:
    application.register_blueprint(blueprint)

# Register Flask Restless blueprints
for model in models:
    # https://github.com/jfinkels/flask-restless/pull/436
    model.__tablename__ = model.__table__.name
    blueprint = manager.create_api_blueprint(model, url_prefix = '/api/raw', results_per_page=100, max_results_per_page=10000, methods=['GET'])
    application.register_blueprint(blueprint)



#######################
#Real endpoints
#######################



#TODO this should be deleted when the declarative method is brought in
@application.route('/api/raw/<table>', methods=['GET'])
@cross_origin()
def list_all(table):
    """ Generate endpoint to list all data in the tables. """

    application.logger.debug('Table selected: {}'.format(table))
    if table not in tables:
        application.logger.error('Error:  Table does not exist.')
        abort(404)

    #Query the database
    conn = engine.connect()
    q = 'SELECT row_to_json({}) from {} limit 1000;'.format(table, table)
    proxy = conn.execute(q)
    results = [x[0] for x in proxy.fetchmany(1000)] # Only fetching 1000 for now, need to implement scrolling
    #print(results)
    conn.close()

    return jsonify(objects=results)


@application.route('/api/meta', methods=['GET'])
@cross_origin()
def get_meta():
    '''
    Outputs the meta.json to the front end
    '''

    conn = engine.connect()
    result = conn.execute("SELECT meta FROM meta")
    row = result.fetchone()
    return row[0]


##########################################
# Start the app
##########################################

if __name__ == "__main__":
    try:
        application.run(host="0.0.0.0", debug=True)
    except:
        conn.close()
