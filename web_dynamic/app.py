#!/usr/bin/python3
"""
Main application file to set up and run the Flask application.
"""

from flask import Flask
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
password = quote(getenv("MYSQL_ROOT_PWD", ''))
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://root:{password}@localhost/teafarm_dev_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)


migrate = Migrate(app, db)


# Initialize database
init_app(app)

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "public_bp.signin"



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
