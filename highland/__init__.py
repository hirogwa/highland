import flask
from highland import settings
app = flask.Flask(__name__)
app.config.from_object('highland.settings_dev')
app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE

import highland.web
