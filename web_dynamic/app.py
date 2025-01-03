#!/usr/bin/python3
"""
Main application file to set up and run the Flask application.
"""

from web_dynamic.routes.public_routes import public_bp
from web_dynamic.routes.employee_routes import employee_bp
from web_dynamic.routes.farmer_routes import farmer_bp
from flask_jwt_extended import JWTManager
from web_dynamic.routes.api.production_api_routes import production_bp
from web_dynamic.routes.api.expense_api_routes import expense_bp
from web_dynamic.routes.api.inventory_api_routes import inventory_bp
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

def create_app():
    """
    Factory function to initialize the Flask app with configuration, blueprints, and extensions.
    """
    # Initialize Flask app
    app = Flask(__name__, static_folder='../web_static')
    app.secret_key = secrets.token_hex(32)

    BLACKLIST = set()
    # Initialize SQLAlchemy
    password = quote(getenv("MYSQL_ROOT_PWD", ''))
    app.config['SQLALCHEMY_DATABASE_URI'] =\
            f'mysql://dev_user:Teafarm2025!@localhost/teafarm_dev_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

    # Initialize Migrate
    migrate = Migrate(app, db)

    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    
    # Disable CSRF protection for API routes
    csrf.exempt(production_bp)
    csrf.exempt(expense_bp)
    csrf.exempt(inventory_bp)

    # Initialize JWTManager
    app.config['JWT_SECRET_KEY'] = secrets.token_hex(32)
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']
    jwt = JWTManager(app)

    # Initialize LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "public_bp.signin"

    # Initialize Database
    init_app(app)

    # Register Blueprints
    app.register_blueprint(production_bp, url_prefix='/api')
    app.register_blueprint(expense_bp, url_prefix='/api')
    app.register_blueprint(farmer_bp, url_prefix='/farmer')
    app.register_blueprint(employee_bp, url_prefix='/employee')
    app.register_blueprint(public_bp)
    app.register_blueprint(inventory_bp, url_prefix='/api')

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

    return app

# If running the app directly, use create_app to get the app instance
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5004)
