import json

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restless import APIManager
from flask import jsonify
from flask.json import JSONEncoder
from datetime import datetime, date


app = Flask(__name__)


with open('secrets.json') as f:
    secrets = json.load(f)
    connect_str = secrets['docker_database']['connect_str']


app.config['SQLALCHEMY_DATABASE_URI'] = connect_str

db = SQLAlchemy(app)



class MedianRent(db.Model):
	__tablename__ = 'acs_rent_median'

	tract_id = db.Column('geo_id2', db.Text, db.ForeignKey('census_mapping.acs_code'), primary_key=True)
	median_rent = db.Column('median_rent', db.Integer)

	tract = db.relationship("CensusMapping", uselist=False, backref='median_rent')

class Project(db.Model):
	__tablename__ = 'project'

	nlihc_id = db.Column('nlihc_id', db.Text, primary_key=True)
#	total_units = db.Column('proj_units_tot', db.Integer)
	min_assisted_units = db.Column('proj_units_assist_min', db.Integer)
	latitude = db.Column('proj_lat', db.Float)
	longitude = db.Column('proj_lon', db.Float)	

class CensusMapping(db.Model):
	__tablename__ = 'census_mapping'

	acs_code = db.Column('acs_code', db.Text, primary_key=True)
	tract_code = db.Column('tract_code', db.Text)

	# median_rent = db.relationship(MedianRent, backref='tract')
	#projects = db.relationship("Project", uselist=True, back_populates='tract')

manager = APIManager(app, flask_sqlalchemy_db=db)

manager.create_api(MedianRent, methods=['GET']) #, serializer=lambda obj: {'tract_id': obj.tract_id, 'median_rent': obj.median_rent}
manager.create_api(Project, methods=['GET'])
manager.create_api(CensusMapping, methods=['GET'])

@app.route('/')
def hello():
    return("The Housing Insights API Rules!")


if __name__ == '__main__':
	app.run()
