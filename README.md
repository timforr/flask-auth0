Flask Auth0 Example
-------------------

.. image:: https://travis-ci.org/sandtable/flask-auth0.svg?branch=master
    :target: http://travis-ci.org/sandtable/flask-auth0
    :alt: Build Status
.. image:: https://codecov.io/github/sandtable/flask-auth0/coverage.svg?branch=master
    :target: https://codecov.io/github/sandtable/flask-auth0?branch=master
    :alt: Code Coverage

Auth0 Flask extension

# Example

```python
from flask import Flask
from flask_auth0 import Auth0

app = Flask()

app.config['AUTH0_CALLBACK_URL'] = ...
app.config['AUTH0_LOGOUT_URL'] = ...
app.config['AUTH0_CLIENT_ID'] = ...
app.config['AUTH0_CLIENT_SECRET'] = ...
app.config['AUTH0_DOMAIN'] = ...
app.config['AUTH0_AUDIENCE'] = ...

auth0 = Auth0()
auth0.init_app(app)
```
