'''
app.py
------

This file contains the logic for the back end of the housing-insights tool.

It does three things:

    1. Auto loads data from Open Data DC (crime and permit) and creates the
    zone facts table every morning. It emails reports of this to CNHED staff.
    2. Allows CNHED staff to load other tables with the newest data.
    3. Sends data from the database as JSON for the front end tool.

The endpoints for the front end are:
    - project
        - All projects.
        - A single project.
        - A single project's subsidies.
    - filter
        - Basically all information.
    - zone_facts
        - The zone facts table for a specific zone.

The project endpoint is created from the models.py and schemas.py files.
The filter endpoint is created by the filter_view_query.py file
The zone facts endpoint is created in this file.
'''
# Application Configuration
import datetime
from mailer import send_mail
from flask import Flask, jsonify, request
from flask_cors import cross_origin
from flask_apscheduler import APScheduler

# Loading
import ETL

# Database
from sqlalchemy import create_engine
from ETL.utils import get_credentials, basic_query

app = Flask(__name__)
app.config['SCHEDULER_API_ENABLED'] = True
scheduler = APScheduler()
scheduler.init_app(app)
engine = create_engine(get_credentials('engine-string'))

# ETL Functions To load DB Tables
table_loaders = {
        'acs': ETL.load_acs_data,
      'crime': ETL.load_crime_data,
     'permit': ETL.load_permit_data,
    'project': ETL.load_project_data,
    'subsidy': ETL.load_subsidy_data,
    'zone_facts': ETL.make_zone_facts,
    'wmata': ETL.make_wmata_tables,
    'raw_wmata': ETL.load_raw_wmata,
}

@app.route('/', methods=['GET'])
def index():
    '''Default page of the API.'''
    return 'At the housing-insights back-end.'

@app.route('/site-map', methods=['GET'])
def site_map():
    '''Returns the possible routes of the app.'''
    return jsonify([str(rule) for rule in app.url_map.iter_rules() 
        if 'GET' in rule.methods])

### API SECTION

@cross_origin()
@app.route('/new_project/<string:nlihc_id>')
@app.route('/new_project', methods=['GET'])
def project(nlihc_id=None):
    '''Returns a JSON of projects (includes TOPA and REAC).'''
    where = f" WHERE nlihc_id = '{nlihc_id}'" if nlihc_id else ''
    result = basic_query('SELECT * FROM new_project'+where+';')
    return jsonify({'objects': result})

@cross_origin()
@app.route('/new_project/<nlihc_id>/subsidies/', methods=['GET'])
def project_subsidies(nlihc_id):
    '''Returns every subsidy associated with a single project.'''
    result = basic_query(f"SELECT * FROM new_subsidy WHERE nlihc_id = '{nlihc_id}';")
    return jsonify({'objects': result})

@cross_origin()
@app.route('/new_filter')
def filter():
    '''Returns a JSON of projects combined with subsidy and zone_facts data.'''
    result = basic_query(ETL.filter_query)
    return jsonify({'objects': result})

@cross_origin()
@app.route('/new_zone_facts/<column_name>/<grouping>', methods = ['GET'])
def zone_facts(column_name='poverty_rate', grouping='ward'):
    '''
    API endpoint to return a single column from zone_facts for a given zone.
    '''
    try:
        if grouping not in ['ward', 'tract', 'neighborhood_cluster']:
            if grouping == 'census_tract':
                grouping = 'tract'
            else:
                raise ValueError('Not valid grouping')
                result = basic_query('''
                       SELECT zone, {}
                         FROM new_zone_facts
                        WHERE zone_type = '{}'
                     ORDER BY zone;'''.format(column_name, grouping))
                status = 'success'
    except:
        result = []
        status = 'Not found'

    output = {'status': status, 'grouping': grouping, 'column_name': column_name, 'objects': result}
    return jsonify(output)

### WMATA Distance
@cross_origin()
@app.route('/new_wmata/<nlihc_id>',  methods=['GET'])
def nearby_transit(nlihc_id):
    result = basic_query(f"SELECT * FROM new_wmata_dist WHERE nlihc_id = '{nlihc_id}';")
    result = ETL.wmata_helper(result)
    return jsonify(result)

### Project Distance
@cross_origin()
@app.route('/projects/<dist>', methods=['GET'])
def nearby_projects(dist):
    latitude = request.args.get('latitude', None)
    longitude = request.args.get('longitude', None)
    if not (latitude and longitude):
        return "Please supply latitude and longitude"
    return jsonify(ETL.nearby_projects(
        float(dist), float(latitude), float(longitude)))


### TABLE LOADING SECTION

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
                <li>wmata</li>
                <li>raw_wmata</li>
            </ul>
               '''
    # Returns True if successfully loaded.
    if table_loaders[table_name](engine):
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
    if ETL.load_crime_data(engine):
        message += "Crime table load successful.\n"
    else:
        message += "Crime table load not successful. Using backup.\n"
    if ETL.load_permit_data(engine):
        message += "Permit table load successful.\n"
    else:
        message += "Permit table load not successful. Using backup.\n"
    if ETL.make_zone_facts(engine):
        message += "Zone facts table creation successful.\n"
    else:
        message += "Zone facts table creation not successful. Using backup.\n"
    send_mail(message)

if __name__ == "__main__":
    print("RUNNING APP")
    scheduler.start()
    app.run(host="0.0.0.0", debug=True)
