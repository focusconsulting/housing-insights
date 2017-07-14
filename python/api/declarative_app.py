from datetime import datetime, date
import json

from flask import Flask, jsonify
from flask.json import JSONEncoder
from flask_restless import APIManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import Boolean, Column, Date, DateTime, Integer, MetaData, Numeric, Table, Text

import logging
logging.basicConfig(level=logging.DEBUG)

with open('secrets.json') as f:
    secrets = json.load(f)
    connect_str = secrets['docker_database']['connect_str']

application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = connect_str
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(application)
Base = automap_base()

metadata = MetaData(bind=db)

Base.prepare(db.engine, reflect=True)

db.session.commit()

BuildingPermits = Base.classes.building_permits
Census = Base.classes.census
CensusMarginOfError = Base.classes.census_margin_of_error
Crime = Base.classes.crime
DcTax = Base.classes.dc_tax
Project = Base.classes.project
ReacScore = Base.classes.reac_score
RealProperty = Base.classes.real_property
Subsidy = Base.classes.subsidy
Topa = Base.classes.topa
WmataDist = Base.classes.wmata_dist
WmataInfo = Base.classes.wmata_info

models = [BuildingPermits, Census, CensusMarginOfError, Crime, DcTax, Project, ReacScore,
          RealProperty, Subsidy, Topa, WmataDist, WmataInfo
          ]

db.init_app(application)


manager = APIManager(application, flask_sqlalchemy_db=db)

for model in models:
    # https://github.com/jfinkels/flask-restless/pull/436
    model.__tablename__ = model.__table__.name
    manager.create_api(model, methods=['GET'])


@application.route('/')
def hello():
    return("The Housing Insights API Rules!")


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=5000)
