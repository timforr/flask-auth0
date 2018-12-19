# Created by Samuel Lesuffleur 15-11-2017
#
# Copyright (c) 2017 Sandtable Ltd. All rights reserved.
import pytest

from flask import Flask
from flask_auth0 import Auth0

AUTH0_CONFIG = {
    'AUTH0_CLIENT_ID': 'id',
    'AUTH0_CLIENT_SECRET': 'secret',
    'AUTH0_DOMAIN': 'test.auth0.com',
    'AUTH0_CALLBACK_URL': '/callback',
    'AUTH0_LOGOUT_URL': '/',
}

_RESP_INDEX = b'too many secrets'
_RESP_PROTECTED = b'protected resource'


def _create_app(config):
    app = Flask(__name__)
    app.secret_key = 'very secret'
    app.config.update(config)
    auth0 = Auth0(app)

    def _make_response(response):
        return response, 200, {
            'Content-Type': 'text/plain; charset=utf-8'
        }

    def _get_index():
        return _make_response(_RESP_INDEX)

    def _get_protected():
        return _make_response(_RESP_PROTECTED)

    def _get_at():
        return _make_response(auth0.access_token)

    app.route('/')(_get_index)
    app.route('/protected')(auth0.requires_auth(_get_protected))
    app.route('/at')(auth0.requires_auth(_get_at))

    return app


@pytest.fixture
def app(request):
    config = {
        'TESTING': True,
    }
    config.update(AUTH0_CONFIG)
    app = _create_app(config=config)

    with app.app_context():
        yield app


@pytest.fixture
def client(request, app):

    client = app.test_client()

    def teardown():
        pass

    request.addfinalizer(teardown)

    return client


def test_index(client, app):
    """Dummy test."""
    resp = client.get('/')
    assert resp.data == _RESP_INDEX


def test_login_logout(mocker, client, app):
    """Test login, logout."""

    resp1 = client.get('/protected')
    assert resp1.status_code == 302
