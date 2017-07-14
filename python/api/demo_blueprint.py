from flask import Blueprint


demo_blueprint = Blueprint('demo_blueprint', __name__, url_prefix='/api/demo')

@demo_blueprint.route('/')
def admin_index():
    return "I'm a demo"

@demo_blueprint.route('/settings')
def settings():
    return 'Settings'
