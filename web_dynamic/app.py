#!/usr/bin/python3
"""
Main application file to set up and run the Flask application.
"""

import secrets
from datetime import timedelta
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from os import getenv
from urllib.parse import quote
from models import db, init_app
from web_dynamic.routes.api.production_api_routes import api_bp
from web_dynamic.routes.farmer_routes import farmer_bp
from web_dynamic.routes.employee_routes import employee_bp
from web_dynamic.routes.public_routes import public_bp

def create_app():
    """
    Factory function to initialize the Flask app with configuration, blueprints, and extensions.
    """
    # Initialize Flask app
    app = Flask(__name__, static_folder='../web_static')
    app.secret_key = secrets.token_hex(32)

    # Configure SQLAlchemy
    password = quote(getenv("MYSQL_ROOT_PWD", ''))
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'mysql://dev_user:Teafarm2025!@localhost/teafarm_dev_db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

    # Initialize extensions
    migrate = Migrate(app, db)
    csrf = CSRFProtect(app)
    csrf.exempt(api_bp)  # Disable CSRF protection for API routes

    # Configure JWTManager
    app.config['JWT_SECRET_KEY'] = getenv('JWT_SECRET_KEY', secrets.token_hex(32))
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    jwt = JWTManager(app)

    # Blacklist set to store invalidated tokens
    BLACKLIST = set()

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_payload):
        """
        Function to check if a token is in the blacklist.
        """
        return jwt_payload['jti'] in BLACKLIST

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """
        Callback for invalid token.
        """
        return jsonify({"message": "Invalid token"}), 401

    # Initialize LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "public_bp.signin"

    @login_manager.user_loader
    def load_user(user_id):
        """
        Load user from database by ID.
        """
        from models.employee import Employee
        from models.farmer import Farmer

        user = Employee.query.get(user_id) or Farmer.query.get(user_id)
        return user

    # Initialize database
    init_app(app)

    # Register Blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(farmer_bp, url_prefix='/farmer')
    app.register_blueprint(employee_bp, url_prefix='/employee')
    app.register_blueprint(public_bp)

    return app


# If running the app directly, use create_app to get the app instance
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5004)
