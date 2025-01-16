#!/usr/bin/python3
"""
Main application file to set up and run the Flask application.
"""

from flask_jwt_extended import JWTManager
from web_dynamic.routes.api_routes import api_bp
from flask import Flask, jsonify
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import secrets
from models import db, init_app
from os import getenv
from urllib.parse import quote
from datetime import timedelta
from flask_migrate import Migrate

app = Flask(__name__, static_folder='../web_static')
app.secret_key = secrets.token_hex(32)

# Initialize SQLAlchemy
password = quote(getenv("TEAFARM_MYSQL_PWD", ''))
# app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{user}:{password}@{host}/{database}'
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+mysqldb://{getenv('TEAFARM_MYSQL_USER')}:{password}@{getenv('TEAFARM_MYSQL_HOST')}/{getenv('TEAFARM_MYSQL_DB')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

migrate = Migrate(app, db)

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Register API Blueprint
app.register_blueprint(api_bp, url_prefix='/api')
# Disable CSRF protection for API routes
csrf.exempt(api_bp)

# Initialize JWTManager
app.config['JWT_SECRET_KEY'] = getenv('JWT_SECRET_KEY' ,secrets.token_hex(32))
app.config['JWT_TOKEN_LOCATION'] = ['headers']  # Tokens will be passed via headers
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

jwt = JWTManager(app)

# Blacklist set to store invalidated tokens
BLACKLIST = set()

# Initialize database
init_app(app)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "public_bp.signin"


# Token blacklist function
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    """
    Function to check if a token is in the blacklist.
    """
    return jwt_payload['jti'] in BLACKLIST

# Invalid token
@jwt.invalid_token_loader
def invalid_token_callback(error):
    """
    Callback for invalid token.
    """
    return jsonify({"message": "Invalid token"}), 401

# User loader function
@login_manager.user_loader
def load_user(user_id):
    from models.employee import Employee
    from models.farmer import Farmer
    # Try to load user as Employee first
    user = Employee.query.get(user_id)
    if user:
        return user

    # If not found as Employee, try Farmer
    user = Farmer.query.get(user_id)
    return user

# Register Blueprints
from web_dynamic.routes.farmer_routes import farmer_bp
from web_dynamic.routes.employee_routes import employee_bp
from web_dynamic.routes.public_routes import public_bp

app.register_blueprint(farmer_bp, url_prefix='/farmer')
app.register_blueprint(employee_bp, url_prefix='/employee')
app.register_blueprint(public_bp)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5004)
