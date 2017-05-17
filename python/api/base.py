from flask_sqlalchemy import SQLAlchemy
import json

with open('secrets.json') as f:
    secrets = json.load(f)
    connect_str = secrets['docker_database']['connect_str']


db = SQLAlchemy()

Base = db.Model

Column = db.Column
Text = db.Text
Integer = db.Integer
Float = db.Float
relationship = db.relationship
ForeignKey = db.ForeignKey