# Created by Samuel Lesuffleur 29-09-2017
#
# Copyright (c) 2017 Sandtable Ltd. All rights reserved.
"""
    Flask-Auth0 is an extension for Flask that allows you to authenticate
    through Auth0 service.
"""
import json
import logging
from functools import wraps
from six.moves.urllib.parse import urlencode, urlparse
from six.moves.urllib.request import urlopen
import time

import flask
from flask import current_app
from flask_oauthlib.client import OAuth
# TODO do not depend on a flask extension
from jose import jwt

logger = logging.getLogger(__name__)


SILENT_AUTH_ERROR_CODES = (
    'login_required',
    'interaction_required',
    'consent_required',
)


class AuthError(Exception):
    def __init__(self, error, status_code=401):
        self.error = error
        self.status_code = status_code


class Auth0(object):
    """The core Auth0 client object."""

    def __init__(self, app=None):
        self._server = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Do setup required by a Flask app."""
        app.config.setdefault('AUTH0_ALGORITHMS', 'RS256')
        app.config.setdefault('AUTH0_AUDIENCE', None)
        app.config.setdefault('AUTH0_CALLBACK_URL', None)
        app.config.setdefault('AUTH0_CLIENT_ID', None)
        app.config.setdefault('AUTH0_CLIENT_SECRET', None)
        app.config.setdefault('AUTH0_DOMAIN', None)
        app.config.setdefault('AUTH0_LOGOUT_URL', None)
        app.config.setdefault('AUTH0_ENABLE_SILENT_AUTHENTICATION', False)
        app.config.setdefault('AUTH0_REQUIRE_VERIFIED_EMAIL', True)
        app.config.setdefault('AUTH0_SESSION_JWT_PAYLOAD', 'jwt_payload')
        app.config.setdefault('AUTH0_SESSION_TOKEN', 'auth0_token')
        app.config.setdefault('AUTH0_SCOPE', 'openid profile email')

        @app.errorhandler(AuthError)
        def handle_auth_error(ex):
            response = flask.jsonify(ex.error)
            response.status_code = ex.status_code
            return response

        token_params = {
            'scope': app.config['AUTH0_SCOPE'].split(' '),
            'audience': app.config['AUTH0_AUDIENCE'],
        }

        server = OAuth(app).remote_app(
            'auth0',
            consumer_key=app.config['AUTH0_CLIENT_ID'],
            consumer_secret=app.config['AUTH0_CLIENT_SECRET'],
            request_token_params=token_params,
            base_url='https://{}'.format(app.config['AUTH0_DOMAIN']),
            access_token_method='POST',
            access_token_url='/oauth/token',
            authorize_url='/authorize',
        )

        @server.tokengetter
        def get_auth0_token():
            return flask.session.get(current_app.config['AUTH0_SESSION_TOKEN'])

        self._server = server

        route = urlparse(app.config['AUTH0_CALLBACK_URL']).path
        app.route(route)(self._callback)

    def _callback(self):
        """Redirect to the originally requested page."""
        args = flask.request.args.to_dict(flat=True)
        try:
            state = json.loads(args['state'])
            next_endpoint = state['destination']
            silent_auth = state['silent_auth']
        except (ValueError, KeyError) as e:
            logger.exception(e)
            raise AuthError('Invalid response callback')

        resp = self._server.authorized_response()
        if resp is None:
            error_code = flask.request.args['error']
            error_desc = flask.request.args['error_description']

            if silent_auth is True and error_code in SILENT_AUTH_ERROR_CODES:
                logger.warning('silent authentication failed: `{}`'
                               .format(error_code))
                return self._redirect_to_auth_server(next_endpoint,
                                                     silent=False)

            error_message = "Not authorized: code='{}', desc='{}'".format(
                error_code, error_desc)
            raise AuthError(error_message)

        id_token = resp['id_token']
        access_token = resp['access_token']

        auth0_domain = current_app.config['AUTH0_DOMAIN']
        auth0_issuer = "https://{}/".format(auth0_domain)
        auth0_algorithms = current_app.config['AUTH0_ALGORITHMS']
        auth0_client_id = current_app.config['AUTH0_CLIENT_ID']
        verify_email = current_app.config['AUTH0_REQUIRE_VERIFIED_EMAIL']

        # check that the JWT is well formed and validate the signature
        # TODO use the requests library to do the request
        # TODO CACHE the jwks?
        # TODO could be done at startup?
        jwks = urlopen("https://{}/.well-known/jwks.json".format(auth0_domain))
        payload = jwt.decode(id_token, jwks.read(),
                             algorithms=auth0_algorithms,
                             audience=auth0_client_id,
                             issuer=auth0_issuer)
        logger.debug('payload: `{}`'.format(json.dumps(payload, indent=4)))

        if verify_email and not payload.get('email_verified', False):
            raise AuthError('Email not verified')

        # TODO validate the claims ?

        # TODO check the permissions ?

        flask.session[current_app.config['AUTH0_SESSION_TOKEN']] = \
            (access_token, '')
        flask.session[current_app.config['AUTH0_SESSION_JWT_PAYLOAD']] = \
            payload

        next_url = flask.url_for(
            next_endpoint, _external=True,
            _scheme=current_app.config['PREFERRED_URL_SCHEME'])
        logger.debug('redirecting to `{}`'.format(next_url))
        return flask.redirect(next_url)

    def _redirect_to_auth_server(self, destination, silent=None):
        """Redirect to the auth0 server.

        Args:
           destination: URL to redirect user
           silent: Do silent authentication?
        """

        state = {'destination': destination}
        params = dict()

        do_silent_auth = (
            silent if silent is not None else
            current_app.config['AUTH0_ENABLE_SILENT_AUTHENTICATION']
        )

        if do_silent_auth:
            params['prompt'] = 'none'
        state['silent_auth'] = do_silent_auth

        logger.debug('redirecting to auth0 authorize uri')

        return self._server.authorize(
            callback=current_app.config['AUTH0_CALLBACK_URL'],
            state=json.dumps(state),
            **params
        )

    def requires_auth(self, view_func):
        """Decorates view functions that require a user to be logged in."""
        @wraps(view_func)
        def decorated(*args, **kwargs):
            # TODO check that the token is still valid

            payload = flask.session.get(
                current_app.config['AUTH0_SESSION_JWT_PAYLOAD'], None)

            if not payload:
                logger.debug('user requires authentication')
                return self._redirect_to_auth_server(flask.request.endpoint)

            if int(time.time()) >= int(payload['exp']):
                logger.debug('token is expired')
                return self._redirect_to_auth_server(flask.request.endpoint)

            logger.debug('user is authenticated')
            return view_func(*args, **kwargs)

        return decorated

    def logout(self):
        """Logout user.

        Request the browser to clear the current session and also clear the
        Auth0 session (clearing the SSO cookie).

        The user won't be log out from a third party Identity Provider.

        The user is redirected to the logout callback.
        """
        flask.session.clear()
        params = {
            'returnTo': current_app.config['AUTH0_LOGOUT_URL'],
            'client_id': current_app.config['AUTH0_CLIENT_ID'],
        }

        url = self._server.base_url + '/v2/logout?' + urlencode(params)
        logger.debug('redirecting to `{}`'.format(url))
        return flask.redirect(url)

    @property
    def access_token(self):
        """Get access token (user must be authenticated)."""
        auth0_token = flask.session.get(
            current_app.config['AUTH0_SESSION_TOKEN'])
        if not auth0_token:
            return None
        return auth0_token[0]

    @property
    def jwt_payload(self):
        """Get JWT payload (user must be authenticated)."""
        return flask.session.get(
            current_app.config['AUTH0_SESSION_JWT_PAYLOAD'],
            None)
