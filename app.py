# Import from system libraries
from flask import Flask, render_template
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api

# Import from application modules
from errors import errors
from models.User import User
from models.db import initialize_db
from routes.api import initialize_routes

from flask_swagger_ui import get_swaggerui_blueprint

# Flask app instance with static (html, css and js) folder configuration
app = Flask(__name__)
# Flask Restful configuration with errors included
api = Api(app, errors=errors)
# Files for Configuration System in environment
app.config.from_envvar('ENV_FILE_LOCATION')
# BCrypt instances
bcrypt = Bcrypt(app)
# JWT instances
jwt = JWTManager(app)
# CORS enabled
CORS(app)


# Get roles for authenticated user
@jwt.user_claims_loader
def add_claims_to_access_token(user):
    return {'roles': user.roles}


# Load user identity
@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.username


# Database Configuration Initialization
initialize_db(app)
# API (Routing) Configuration Initialization
initialize_routes(api)

# Admin account initialization for first uses
user = User.objects(username='admin@nj.net')
if not user:
    login = User(username='admin@nj.net', password='enje123', roles=['admin'])
    login.hash_password()
    login.save()

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swagger.json'  # Our API url (can of course be a local resource)
# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Employee Management System"
    },
    # oauth_config={  # OAuth config. See https://github.com/swagger-api/swagger-ui#oauth2-configuration .
    #    'clientId': "your-client-id",
    #    'clientSecret': "your-client-secret-if-required",
    #    'realm': "your-realms",
    #    'appName': "your-app-name",
    #    'scopeSeparator': " ",
    #    'additionalQueryStringParams': {'test': "hello"}
    # }
)
app.register_blueprint(swaggerui_blueprint)

# Running Flask Application when main class executed
if __name__ == '__main__':
    app.run()
