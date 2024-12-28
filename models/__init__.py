#!/usr/bin/python3
"""
Initialize the models package
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app(app):
    # Bind the SQLAlchemy object to the app
    db.init_app(app)

    # Import models here to avoid circular imports
    from .employee import Employee
    from .farmer import Farmer
    from .inventory import Inventory
    from .labour import Labour
    from .market_value import MarketValue
    from .production import ProductionRecord
    from .sales import DailySales
    from .expense import Expense
    from .task import Task
    from .daily_production_summary import DailyProductionSummary

    # Create all tables (optional, remove if migrations are used)
    with app.app_context():
        db.create_all()
