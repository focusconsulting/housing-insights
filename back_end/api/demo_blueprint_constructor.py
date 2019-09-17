from flask import Blueprint

def construct_demo_blueprint(choice):

    demo_blueprint = Blueprint('constructed', __name__, url_prefix='/api/constructed_demo')

    @demo_blueprint.route('/')
    def admin_index():
        return "I'm a demo. Your choice was {}".format(choice)

    @demo_blueprint.route('/settings')
    def settings():
        return 'Settings'

    return demo_blueprint