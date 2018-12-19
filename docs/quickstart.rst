.. _quickstart:

Quickstart
==========

Here is a Hello World example.

You will need to set your Auth0 domain and Application Client ID and Secret.

.. code-block:: python

    from flask import Flask, jsonify

    from flask_auth0 import Auth0

    app = Flask(__name__)

    app.secret_key = 'secret'

    app.config['AUTH0_LOGOUT_URL'] = 'http://localhost:3000/logout'
    app.config['AUTH0_CALLBACK_URL'] = 'http://localhost:3000/callback'
    app.config['AUTH0_DOMAIN'] = '<your company>.eu.auth0.com'
    app.config['AUTH0_CLIENT_ID'] = 'YOUR_AUTH0_CLIENT_ID'
    app.config['AUTH0_CLIENT_SECRET'] = 'YOUR_AUTH0_CLIENT_SECRET'

    auth0 = Auth0()
    auth0.init_app(app)

    @app.route('/')
    @auth0.requires_auth
    def hello():
        return 'Hello world!'

    @app.route('/logout')
    @auth0.requires_auth
    def logout():
        auth0.logout()
        return jsonify('logout')


    if __name__ == '__main__':
        app.run(port=3000)

Save this snippet as `hello_world.py` and add your required Auth0 configuration.

To run the example:

.. code-block:: console

    $ python hello_world.py

Then browse to http://localhost:3000 and sign in.

You can logout by navigating to: http://localhost:3000/logout
