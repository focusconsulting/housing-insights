# -*- coding: utf-8 -*-

"""
flask api
~~~~~~~~~
This is a simple Flask application that creates SQL query endpoints.

"""

from flask import Flask, jsonify, request, Response, abort
import psycopg2
import logging

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

conn = psycopg2.connect('dbname=housinginsights_docker user=codefordc password=codefordc host=localhost port=5432')

with conn.cursor() as cur:
    q = "SELECT tablename FROM pg_catalog.pg_tables where schemaname = 'public'"
    cur.execute(q)
    tables = [x[0] for x in cur.fetchall()]
    app.logger.debug('Database tables: {}'.format(tables))


@app.route('/api/<table>', methods=['GET'])
def list_all(table):
    """ Generate endpoint to list all data in the tables. """

    app.logger.debug('Table selected: {}'.format(table))
    if table not in tables:
        app.logger.error('Error:  Table does not exist.')
        abort(404)
    with conn.cursor() as cur:
        q = 'SELECT row_to_json({}) from {};'.format(table, table)
        cur.execute(q)
        # Only fetching 100 for now, need to implement scrolling
        results = [x[0] for x in cur.fetchmany(100)]

    return jsonify(items=results)


@app.route('/api/building_permits/<zipcode>', methods=['GET'])
def count_per_zip(zipcode):
    """ Example endpoint of doing a COUNT on a specific zipcode. """

    app.logger.debug('Zip selected: {}'.format(zipcode))
    with conn.cursor() as cur:
        q = "SELECT COUNT(*) FROM building_permits WHERE zipcode = '{}'".format(zipcode)
        cur.execute(q)
        results = cur.fetchall()[0][0]

    return jsonify({'count': results})


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", debug=True)
    except:
        conn.close()
