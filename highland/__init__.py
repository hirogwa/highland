import flask
app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'postgresql+psycopg2://localhost:5432/highland')

import highland.web
