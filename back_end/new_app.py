'''new_app.py'''

from config import Config
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
ma = Marshmallow(app)

import models
import schemas

@app.route('/', methods=['GET'])
def index():
    '''Default page of the API.'''
    return 'At the housing-insights back-end.'

@app.route('/project')
def project():
    '''
    Returns a JSON of projects (see NewProjectSchema):
    '''
    projects = models.NewProject.query.all()
    result = schemas.new_project_schema.dump(projects)
    return jsonify(result)

@app.route('/filter')
def filter():
    '''
    Returns a JSON of projects (see NewFilterSchema):
    '''
    projects = models.NewProject.query.all()
    result = schemas.new_filter_schema.dump(projects)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
