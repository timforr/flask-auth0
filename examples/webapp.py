# Created by Samuel Lesuffleur 03-10-2017
#
# Copyright (c) 2017 Sandtable Ltd. All rights reserved.
import logging
from gevent.wsgi import WSGIServer
import os

from flask import Flask, Blueprint, jsonify

from flask_auth0 import Auth0
from flask_auth0.api import get_userinfo, requires_auth

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

auth0 = Auth0()
protected = Blueprint('hello', __name__)
not_protected = Blueprint('not_safe', __name__)


@protected.before_request
@auth0.requires_auth
def before_request():
    pass


@protected.route('/')
def hello():
    return 'Hello world!'


@protected.route('/userinfo')
def userinfo():
    resp = auth0.get_userinfo()
    return jsonify(resp.data)


@not_protected.route('/api/userinfo')
@requires_auth
def api_userinfo():
    profile = get_userinfo()
    return jsonify(profile)


@protected.route('/payload')
def payload():
    resp = auth0.jwt_payload
    return jsonify(resp)


@protected.route('/access_token')
def access_token():
    resp = auth0.access_token
    return jsonify(resp)


@protected.route('/logout')
def logout():
    return auth0.logout()


def create_app():
    # TODO separate Webapp and API
    app = Flask(__name__)
    app.secret_key = 'secret'
    app.config['AUTH0_CALLBACK_URL'] = 'http://localhost:3000/callback'
    app.config['AUTH0_LOGOUT_URL'] = 'http://localhost:3000/'
    app.config['AUTH0_CLIENT_ID'] = os.getenv('AUTH0_CLIENT_ID')
    app.config['AUTH0_CLIENT_SECRET'] = os.getenv('AUTH0_CLIENT_SECRET')
    app.config['AUTH0_DOMAIN'] = 'sandtable.eu.auth0.com'
    app.config['AUTH0_AUDIENCE'] = 'https://api.dev.sands.im/'
    app.config['AUTH0_ENABLE_SILENT_AUTHENTICATION'] = True
    app.config['AUTH0_SCOPE'] = 'openid email profile groups roles'

    auth0.init_app(app)

    app.register_blueprint(protected)
    app.register_blueprint(not_protected)
    return app


if __name__ == '__main__':
    app = create_app()

    host, port = ('localhost', 3000)
    logger.info('Serving {}:{}'.format(host, port))

    http_server = WSGIServer((host, port), app)
    http_server.serve_forever()
