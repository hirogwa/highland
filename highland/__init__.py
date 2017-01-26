import flask
app = flask.Flask(__name__)
app.config.from_object('highland.settings_dev')
app.config['SQLALCHEMY_DATABASE_URI'] = app.config.get('DATABASE')

import highland.web
