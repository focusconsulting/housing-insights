'''
app.py

This file contains the logic for the back end of the housing-insights tool.

It does three things:

    1. Auto loads data from Open Data DC (crime and permit) and creates the
    zone facts table every morning. It emails reports of this to CNHED staff.
    2. Allows CNHED staff to load other tables with the newest data.
    3. Sends data from the database as JSON for the front end tool.

The endpoints for the front end are:
    - project
    - filter
    - zone_facts

The project endpoint is created from the models.py and schemas.py files.
The filter endpoint is created by the filter_view_query.py file
The zone facts endpoint is created in this file.
'''
import datetime
from mailer import send_mail
from flask import Flask, jsonify
from flask_cors import cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from flask_marshmallow import Marshmallow
from config import TestingConfig, ProductionConfig
import filter_view_query

app = Flask(__name__)
app.config.from_object(TestingConfig)
db = SQLAlchemy(app)
ma = Marshmallow(app)

scheduler = APScheduler()
scheduler.init_app(app)

import models
import schemas
import ETL
from ETL.utils import get_credentials

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
@app.route('/new_project')
def project():
    '''Returns a JSON of projects (see NewProjectSchema)'''
    projects = models.NewProject.query.all()
    result = schemas.new_project_schema.dump(projects)
    return jsonify({'objects': result})

@cross_origin()
@app.route('/new_filter')
def filter():
    '''Returns a JSON of projects combined with subsidy and zone_facts data.'''
    proxy = db.session.execute(filter_view_query.query)
    result = [dict(x) for x in proxy]
    return jsonify({'objects': result})

@cross_origin()
@app.route('/new_zone_facts/<column_name>/<grouping>', methods = ['GET'])
def zone_facts(column_name = 'poverty_rate', grouping='ward'):
    '''
    API endpoint to return a single column from zone_facts for a given zone.
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
    if password != get_credentials('load-data-password'):
        send_mail('Invalid data loading attempted.')
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
            </ul>
               '''
    # Returns True if successfully loaded.
    if table_loaders[table_name](engine=db.get_engine()):
        send_mail('Loaded {} table.'.format(table_name))
        return '<h1>Success! Loaded {} table.</h1>'.format(table_name)
    return '''
            <h1>Unable to load {} table.</h1>
            <h2>The source data may be unavailable.</h2>
            <h2>Housing insights will load the backup data.</h2>
           '''.format(table_name)

@scheduler.task('cron', id='do_auto_load_tables', day="*", hour=0)
def auto_load_tables():
    '''Grabs the most recent data every morning and puts it in the DB.'''
    print("RELOADING DATA")
    message = "Data update for {}\n".format(datetime.datetime.now())
    if ETL.load_crime_data(engine=db.get_engine()):
        message += "Crime table load successful.\n"
    else:
        message += "Crime table load not successful. Using backup.\n"
    if ETL.load_permit_data(engine=db.get_engine()):
        message += "Permit table load successful.\n"
    else:
        message += "Permit table load not successful. Using backup.\n"
    if ETL.make_zone_facts(db):
        message += "Zone facts table creation successful.\n"
    else:
        message += "Zone facts table creation not successful. Using backup.\n"
    send_mail(message)

if __name__ == "__main__":
    print("RUNNING APP")
    scheduler.start()
    app.run(host="0.0.0.0", debug=False)
