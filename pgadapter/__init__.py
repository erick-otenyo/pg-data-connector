"""PG ADAPTER  MODULE"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import os
import sys

import rollbar
import rollbar.contrib.flask
from flask import Flask, got_request_exception
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from rollbar.logger import RollbarHandler
from pgadapter import db_setup

from pgadapter.config import SETTINGS

logging.basicConfig(
    level=SETTINGS.get('logging', {}).get('level'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y%m%d-%H:%M%p',
)

# Flask App
app = Flask(__name__, template_folder=SETTINGS.get("TEMPLATE_DIR"))
CORS(app)

# Ensure all unhandled exceptions are logged, and reported to rollbar
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

rollbar.init(os.getenv('ROLLBAR_SERVER_TOKEN'), os.getenv('ENV'))
rollbar_handler = RollbarHandler()
rollbar_handler.setLevel(logging.ERROR)
logger.addHandler(rollbar_handler)


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception


@app.before_first_request
def init_rollbar():
    """init rollbar module"""
    rollbar.init(
        SETTINGS.get('ROLLBAR_SERVER_TOKEN'),
        # environment name
        os.getenv('ENV'),
        # server root directory, makes tracebacks prettier
        root=os.path.dirname(os.path.realpath(__file__)),
        # flask already sets up logging
        allow_logging_basic_config=False)

    # send exceptions from `app` to rollbar, using flask's signal system.
    got_request_exception.connect(rollbar.contrib.flask.report_exception, app)


# Config
app.config['SQLALCHEMY_DATABASE_URI'] = SETTINGS.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# pagination
app.config['ITEMS_PER_PAGE'] = SETTINGS.get('ITEMS_PER_PAGE', 20)

# TODO: Run this only once
# Setup Db
db_setup.setup()

# Database
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# DB has to be ready!
from pgadapter.routes.api.v1 import endpoints, error

# Blueprint Flask Routing
app.register_blueprint(endpoints, url_prefix='/api/v1')


@app.errorhandler(403)
def forbidden(e):
    return error(status=403, detail='Forbidden')


@app.errorhandler(404)
def page_not_found(e):
    return error(status=404, detail='Not Found')


@app.errorhandler(405)
def method_not_allowed(e):
    return error(status=405, detail='Method Not Allowed')


@app.errorhandler(410)
def gone(e):
    return error(status=410, detail='Gone')


@app.errorhandler(500)
def internal_server_error(e):
    return error(status=500, detail='Internal Server Error')
