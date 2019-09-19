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

test_schema = schemas.TestSchema(many=True)

@app.route('/', methods=['GET'])
def index():
    '''Default page of the API.'''
    return 'At the housing-insights back-end.'

@app.route('/project')
def project():
    '''
    Returns the following in JSON:
      - nlihc_id
      - latitude
      - longitude
      - proj_name
      - proj_addre
      - ward
      - proj_units_assist_max
      - proj_units_tot
      - subsidy_end_first
      - subsidy_end_last
      - neighborhood_cluster_desc
    '''
    projects = models.NewProject.query.all()
    result = test_schema.dump(projects)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
