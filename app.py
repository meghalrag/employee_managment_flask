# Import from system libraries
from flask import Flask, render_template
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_http_middleware import MiddlewareManager
from middleware.casbin_middleware import CasbinMiddleware

# Import from application modules
from errors import errors
from models.User import User, UserProfile, TokenBlacklist
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

app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = 'access'


# Get roles for authenticated user
@jwt.user_claims_loader
def add_claims_to_access_token(user):
    return {'roles': user.roles}


# Load user identity
@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.username

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(jwt_payload):
    jti = jwt_payload['jti']
    return TokenBlacklist.objects(jti=jti).first() is not None


# Database Configuration Initialization
initialize_db(app)
# API (Routing) Configuration Initialization
initialize_routes(api)

# Manager account initialization for first uses
user = User.objects(username='meghalrag@123.com')
if not user:
    login = User(username='meghalrag@123.com', phone_number="9999999999", password='123', roles=['manager'])
    login.hash_password()
    login.save()
    prof = UserProfile(name="Meghal", email="meghalrag@123.com", phone_number="9999999999", designation="manager", department="All", manager="No Manager")
    prof.user = login
    prof.save()

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

app.wsgi_app = MiddlewareManager(app)
app.wsgi_app.add_middleware(CasbinMiddleware)

# Running Flask Application when main class executed
if __name__ == '__main__':
    app.run()
