#!/usr/bin/env python3
import pytest
from web_dynamic.app import create_app, db
from models.production import ProductionRecord
from models.expense import Expense
from models.employee import Employee
from models.farmer import Farmer
from models.labour import Labour
from flask_jwt_extended import create_access_token
from datetime import date

def setup_database(app):
    """Set up the test database with sample data."""
    db.drop_all()
    db.create_all()

    # Add test farmer
    test_farmer = Farmer(
        name="John Doe",
        email="farmer@test.com",
        phone_number="1234567890",
        password_hash="hashedpassword"
    )
    db.session.add(test_farmer)

    # Add labour categories
    plucking_labour = Labour(
        type="plucking",
        farmer_id=test_farmer.id
    )
    weeding_labour = Labour(
        type="weeding",
        farmer_id=test_farmer.id
    )
    db.session.add(plucking_labour)
    db.session.add(weeding_labour)

    # Add test employee
    test_employee = Employee(
        name="Jane Smith",
        email="employee@test.com",
        phone_number="9876543210",
        job_type_id=plucking_labour.id,
        password_hash="hashedpassword",
        farmer_id=test_farmer.id
    )
    db.session.add(test_employee)

    # Add production records
    production_1 = ProductionRecord(
        employee_id=test_employee.id,
        weight=100.0,
        rate=10.0,
        date=date(2024, 12, 1),
        farmer_id=test_farmer.id
    )
    production_2 = ProductionRecord(
        employee_id=test_employee.id,
        weight=200.0,
        rate= 10.0,
        date=date(2024, 12, 2),
        farmer_id=test_farmer.id
    )
    db.session.add(production_1)
    db.session.add(production_2)

    # Add expense
    expense = Expense(
        category_id=weeding_labour.id,
        description="Fertilizer Purchase",
        amount=500.0,
        date=date(2024, 12, 1),
        farmer_id=test_farmer.id
    )
    db.session.add(expense)
    db.session.commit()

    return test_farmer, test_employee, [production_1, production_2], expense, plucking_labour, weeding_labour


def test_total_production_report():
    """Test generating a total production report for a date range."""
    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        test_farmer, test_employee, productions, expense, *_ = setup_database(app)
        access_token = create_access_token(identity=test_farmer.id)

        payload = {
            "start_date": "2024-12-01",
            "end_date": "2024-12-02"
        }

        with app.test_client() as client:
            response = client.post(
                '/api/reports/total_production',
                json=payload,
                headers={'Authorization': f'Bearer {access_token}'}
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data['total_weight'] == 300.0
            assert data['total_income'] == 4500.0  # 100*15 + 200*15


def test_employee_performance_report():
    """Test generating an employee-specific performance report."""
    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        test_farmer, test_employee, productions, expense, *_ = setup_database(app)
        access_token = create_access_token(identity=test_farmer.id)

        payload = {
            "employee_id": test_employee.id,
            "start_date": "2024-12-01",
            "end_date": "2024-12-02"
        }

        with app.test_client() as client:
            response = client.post(
                '/api/reports/employee_performance',
                json=payload,
                headers={'Authorization': f'Bearer {access_token}'}
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data['employee_name'] == "Jane Smith"
            assert data['total_weight'] == 300.0
            assert data['total_income'] == 4500.0


def test_expense_report():
    """Test generating a report for total expenses within a date range."""
    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        test_farmer, test_employee, productions, expense, *_ = setup_database(app)
        access_token = create_access_token(identity=test_farmer.id)

        payload = {
            "start_date": "2024-12-01",
            "end_date": "2024-12-02"
        }

        with app.test_client() as client:
            response = client.post(
                '/api/reports/expenses',
                json=payload,
                headers={'Authorization': f'Bearer {access_token}'}
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data['total_expenses'] == 500.0
            assert len(data['details']) == 1
            assert data['details'][0]['description'] == "Fertilizer Purchase"
            assert data['details'][0]['amount'] == 500.0


def test_combined_report():
    """Test generating a combined report for production and expenses."""
    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        test_farmer, test_employee, productions, expense, *_ = setup_database(app)
        access_token = create_access_token(identity=test_farmer.id)

        payload = {
            "start_date": "2024-12-01",
            "end_date": "2024-12-02"
        }

        with app.test_client() as client:
            response = client.post(
                '/api/reports/combined',
                json=payload,
                headers={'Authorization': f'Bearer {access_token}'}
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data['total_production'] == 300.0
            assert data['total_income'] == 4500.0
            assert data['total_expenses'] == 500.0
            assert data['net_profit'] == 4000.0
