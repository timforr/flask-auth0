Flask Auth0 Example
-------------------

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
