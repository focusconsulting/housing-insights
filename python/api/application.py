# -*- coding: utf-8 -*-

"""
flask api
~~~~~~~~~
This is a simple Flask applicationlication that creates SQL query endpoints.

"""

from flask import Flask, jsonify, request, Response, abort, json
import psycopg2
import logging

logging.basicConfig(level=logging.DEBUG)
application = Flask(__name__)

with open('secrets.json') as f:
    secrets = json.load(f)
    connect_str = secrets['remote_database']['connect_str']

conn = psycopg2.connect(connect_str)

with conn.cursor() as cur:
    q = "SELECT tablename FROM pg_catalog.pg_tables where schemaname = 'public'"
    cur.execute(q)
    tables = [x[0] for x in cur.fetchall()]
    application.logger.debug('Database tables: {}'.format(tables))

@application.route('/')
def hello():
    return("The Housing Insights API Rules!")

@application.route('/api/<table>', methods=['GET'])
def list_all(table):
    """ Generate endpoint to list all data in the tables. """

    application.logger.debug('Table selected: {}'.format(table))
    if table not in tables:
        application.logger.error('Error:  Table does not exist.')
        abort(404)
    with conn.cursor() as cur:
        q = 'SELECT row_to_json({}) from {};'.format(table, table)
        cur.execute(q)
        # Only fetching 100 for now, need to implement scrolling
        results = [x[0] for x in cur.fetchmany(100)]

    return jsonify(items=results)


@application.route('/api/building_permits/zip/<zipcode>', methods=['GET'])
def count_per_zip(zipcode):
    """ Example endpoint of doing a COUNT on a specific zipcode. """

    application.logger.debug('Zip selected: {}'.format(zipcode))
    with conn.cursor() as cur:
        q = "SELECT COUNT(*) FROM building_permits WHERE zipcode = '{}'".format(zipcode)
        cur.execute(q)
        results = cur.fetchall()[0][0]

    return jsonify({'count': results})
    

@application.route('/api/building_permits/nc/<nc>', methods=['GET'])
def count_per_neighborhood_cluster(nc):
    """ Example endpoint of doing a COUNT on a specific neighborhood cluster. """

    application.logger.debug('Neighborhood cluster selected: {}'.format(nc))
    with conn.cursor() as cur:
        q = "SELECT COUNT(*) FROM building_permits WHERE neighborhoodcluster = '{}'".format(nc)
        cur.execute(q)
        results = cur.fetchall()[0][0]

    return jsonify({'count': results})


@application.route('/api/building_permits/ward/<ward>', methods=['GET'])
def count_per_ward(ward):
    """ Example endpoint of doing a COUNT on a specific ward. """

    application.logger.debug('Ward selected: {}'.format(ward))
    with conn.cursor() as cur:
        q = "SELECT COUNT(*) FROM building_permits WHERE ward = '{}'".format(ward)
        cur.execute(q)
        results = cur.fetchall()[0][0]

    return jsonify({'count': results})


@application.route('/api/building_permits/all/<grouping>', methods=['GET'])
def count_all_zip(grouping):
    """ Example endpoint of doing a COUNT on a specific zipcode. """

    #this query structure will only work for certain filed names
    if grouping not in ['zipcode','ward','anc','neighborhoodcluster']:
        return jsonify({'results': None})

    application.logger.debug('Getting all {}'.format(grouping))

    #COALESCE needs the right data type in the fallback
    fallback = "'Unknown'" if grouping in ['zipcode','anc'] else 0

    with conn.cursor() as cur:
        q = """
            SELECT COALESCE({},{}) --'Unknown'
            ,count(permit_id) AS permits
            FROM building_permits
            where issue_date between '2016-01-01' and '2016-12-31'
            --WHERE report_date BETWEEN (now()::TIMESTAMP - INTERVAL '1 year') AND now()::TIMESTAMP
            GROUP BY {} 
            ORDER BY {}
            """.format(grouping,fallback,grouping,grouping)

        cur.execute(q)
        results = cur.fetchall()
        results = dict(results)

    return jsonify({'results': results})


if __name__ == "__main__":
    try:
        application.run(host="0.0.0.0", debug=True)
    except:
        conn.close()
