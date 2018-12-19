# Created by Samuel Lesuffleur 03-10-2017
#
# Copyright (c) 2017 Sandtable Ltd. All rights reserved.
import logging
from gevent.wsgi import WSGIServer
import os

from flask import Flask, Blueprint, jsonify, request

from flask_auth0 import Auth0
import flask_auth0.management as auth0_mgmt

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

auth0 = Auth0()
mgmt = Blueprint('mgmt', __name__)


@mgmt.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    resp = auth0_mgmt.get_user(user_id)
    return jsonify(resp)


@mgmt.route('/users/<user_id>', methods=['PATCH'])
def update_user(user_id):
    fields = request.get_json(force=True)
    resp = auth0_mgmt.update_user(user_id, fields)
    return jsonify(resp)


def create_app():
    app = Flask(__name__)
    app.secret_key = 'secret'
    app.config['AUTH0_CALLBACK_URL'] = 'http://localhost:3000/callback'
    app.config['AUTH0_LOGOUT_URL'] = 'http://localhost:3000/'
    app.config['AUTH0_CLIENT_ID'] = os.getenv('AUTH0_CLIENT_ID')
    app.config['AUTH0_CLIENT_SECRET'] = os.getenv('AUTH0_CLIENT_SECRET')
    app.config['AUTH0_DOMAIN'] = 'sandtable.eu.auth0.com'
    app.config['AUTH0_AUDIENCE'] = 'https://api.dev.sands.im/'
    app.config['AUTH0_RESOURCE_SERVER_ONLY'] = True

    auth0.init_app(app)
    app.register_blueprint(mgmt)
    return app


if __name__ == '__main__':
    app = create_app()

    host, port = ('localhost', 3000)
    logger.info('Serving {}:{}'.format(host, port))

    http_server = WSGIServer((host, port), app)
    http_server.serve_forever()
