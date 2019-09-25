'''new_app.py'''

from config import Config
from flask import Flask, jsonify
from flask_cors import cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
ma = Marshmallow(app)

import models
import schemas
import ETL

# ETL Functions To load DB Tables
table_loaders = {
        'acs': ETL.load_acs_data,
      'crime': ETL.load_crime_data,
     'permit': ETL.load_permit_data,
    'project': ETL.load_project_data,
    'subsidy': ETL.load_subsidy_data,
}

@app.route('/', methods=['GET'])
def index():
    '''Default page of the API.'''
    return 'At the housing-insights back-end.'

@cross_origin()
@app.route('/project')
def project():
    '''Returns a JSON of projects (see NewProjectSchema)'''
    projects = models.NewProject.query.all()
    result = schemas.new_project_schema.dump(projects)
    return jsonify({'objects': result})

@cross_origin()
@app.route('/filter')
def filter():
    '''Returns a JSON of projects (see NewFilterSchema)'''
    projects = models.NewProject.query.all()
    result = schemas.new_filter_schema.dump(projects)
    return jsonify({'objects': result})

@cross_origin()
@app.route('/zone_facts/<column_name>/<grouping>', methods = ['GET'])
def zone_facts(column_name = 'poverty_rate', grouping='ward'):
    '''
    API endpoint to return just the column and grouping matching the passed
    values, in the format needed by the chloropleth map
    '''
    try:
        proxy = db.session.execute('''
           SELECT zone, {}
             FROM new_zone_facts
            WHERE zone_type = '{}'
         ORDER BY zone;'''.format(column_name, grouping))
        result = [dict(x) for x in proxy]
        status = 'success'
    except:
        result = []
        status = 'Not found'

    output = {'status': status, 'grouping': grouping, 'column_name': column_name, 'objects': result}
    return jsonify(output)

@app.route('/make_table/<table_name>/<password>')
def make_table(table_name, password):
    '''
    This function allows CNHED staff to load a database table "manually".
    See the documentation for clear instructions on creating tables.
    '''
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
    if table_loaders[table_name](engine=db.get_engine()):
        return '<h1>Success! Loaded {} table.</h1>'.format(table_name)
    return '''
            <h1>Unable to load {} table.</h1>
            <h2>The source data may be unavailable.</h2>
            <h2>Housing insights will load the backup data.</h2>
           '''.format(table_name)

@app.route("/test")
def test():
    if ETL.make_zone_facts(db):
        return "DID IT"
    return "DID NOT DO IT"

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
