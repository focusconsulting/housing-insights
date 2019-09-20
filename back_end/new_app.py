'''new_app.py'''

from config import Config
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
#app.config.from_object(Config)
#db = SQLAlchemy(app)
#ma = Marshmallow(app)

#import models
#import schemas

# TODO: Change init in ETL to load functions.
from ETL.sources import load_crime_data, load_permit_data

# ETL Functions To load DB Tables
table_loaders = {
    'crime': load_crime_data,
    'acs': lambda: False,
    'permit': load_permit_data,
    'project': lambda: False,
    'subsidy': lambda: False,
}

@app.route('/', methods=['GET'])
def index():
    '''Default page of the API.'''
    return 'At the housing-insights back-end.'

@app.route('/project')
def project():
    '''Returns a JSON of projects (see NewProjectSchema)'''
    projects = models.NewProject.query.all()
    result = schemas.new_project_schema.dump(projects)
    return jsonify(result)

@app.route('/filter')
def filter():
    '''Returns a JSON of projects (see NewFilterSchema)'''
    projects = models.NewProject.query.all()
    result = schemas.new_filter_schema.dump(projects)
    return jsonify(result)

@app.route('/make_table/<table_name>/<password>')
def make_table(table_name, password):
    '''Loads a table based on the table_name.'''
    if password != "SECRET":
        return '<h1>Invalid Password: Please Try Again</h1>'
    if table_name not in table_loaders.keys():
        return '''
            <h1>Invalid Table Name: Please Try Again</h1>
            <h2>Tables Are:</h2>
            <ul>
                <li>crime</li>
                <li>acs</li>
                <li>permit</li>
                <li>project</li>
                <li>subsidy</li>
            </ul>
               '''
    # Returns True if successfully loaded.
    if table_loaders[table_name]():
        return '<h1>Success! Loaded {} table.</h1>'.format(table_name)
    return '''
            <h1>Unable to load {} table.</h1>
            <h2>The source data may be unavailable.</h2>
            <h2>Housing insights will load the backup data.</h2>
           '''.format(table_name)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
