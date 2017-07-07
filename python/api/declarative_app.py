from flask import Flask
from flask_restless import APIManager
from flask import jsonify
from flask.json import JSONEncoder
from datetime import datetime, date

from models import MedianRent, Project, CensusMapping, Census
from base import db, connect_str

app = Flask(__name__)

db.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = connect_str

manager = APIManager(app, flask_sqlalchemy_db=db)

for model in [MedianRent, Project, CensusMapping, Census]:
    manager.create_api(model, methods=['GET'])


@app.route('/')
def hello():
    return("The Housing Insights API Rules!")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
