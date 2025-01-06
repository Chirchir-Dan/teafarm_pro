#!/usr/bin/env python3
import pytest
import uuid
from datetime import date
from web_dynamic.app import create_app, db
from flask_jwt_extended import create_access_token
from models.expense import Expense
from models.labour import Labour
from models.employee import Employee
from models.farmer import Farmer

def setup_database(app):
    """Set up the test database with sample data."""
    db.drop_all()
    db.create_all()

    
    test_farmer = Farmer(
        name="John Doe",
        email="test@user.com",
        phone_number="123456789",
        password_hash="hashedpassword"
    )
    db.session.add(test_farmer)
    db.session.commit()

    labour_type = Labour(
        type="plucking",
        farmer_id=test_farmer.id
    )
    db.session.add(labour_type)
    db.session.commit()

    # Attach expenses to the test farmer
    expense1 = Expense(
        category_id=labour_type.id,
        description="Test expense 1",
        amount=100.0,
        date=date.today().strftime('%Y-%m-%d'),
        farmer_id=test_farmer.id  # Link expense to the test farmer
    )
    expense2 = Expense(
        description="Plucking expense",
        amount=150.0,
        date=date.today().strftime('%Y-%m-%d'),
        category_id=labour_type.id,
        farmer_id=test_farmer.id  # Link expense to the test farmer
    )
    db.session.add_all([expense1, expense2])
    db.session.commit()

    return test_farmer

def teardown_database(app):
    """Clean up the database after a test."""
    db.session.remove()  # Close any active session
    db.drop_all()

def test_get_expenses():
    """Test getting all expenses."""
    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        test_farmer = setup_database(app)
        access_token = create_access_token(identity=test_farmer.id)

        with app.test_client() as client:
            response = client.get(
                '/api/expenses',
                headers={'Authorization': f'Bearer {access_token}'}
            )

            assert response.status_code == 200
            data = response.get_json()
            assert isinstance(data, list)
            assert len(data) == 2

            assert any(item['description'] == "Plucking expense" and item['amount'] == 150.0 for item in data)
            assert any(item['description'] == "Test expense 1" and item['amount'] == 100.0 for item in data)

def test_get_single_expense():
    """Test getting a single expense record by ID."""
    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        test_farmer = setup_database(app)
        access_token = create_access_token(identity=test_farmer.id)

        expense = db.session.query(Expense).filter_by(farmer_id=test_farmer.id).first()
        assert expense is not None

        with app.test_client() as client:
            response = client.get(
                f'/api/expenses/{expense.id}',
                headers={'Authorization': f'Bearer {access_token}'}
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data['amount'] == expense.amount
            assert data['description'] == expense.description
            assert data['date'] == expense.date.isoformat()

def test_create_expense():
    """Test creating a new expense record."""
    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        test_farmer = setup_database(app)

        labour_type = db.session.query(Labour).filter_by(farmer_id=test_farmer.id).first()

        access_token = create_access_token(identity=test_farmer.id)

        payload = {
            "category_id": labour_type.id,
            "description": "New plucking expense",
            "amount": 200.0,
            "date": date.today().strftime('%Y-%m-%d'),
            "farmer_id": test_farmer.id
        }

        with app.test_client() as client:
            response = client.post(
                '/api/expenses',
                json=payload,
                headers={'Authorization': f'Bearer {access_token}'}
            )

            print(response.data)
            assert response.status_code == 201
            data = response.get_json()
            assert data['amount'] == 200.0
            assert data['description'] == "New plucking expense"
            assert data['date'] == date.today().isoformat()


def test_update_expense():
    """Test updating an existing expense record."""
    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        test_farmer = setup_database(app)
        assert test_farmer.id is not None
        access_token = create_access_token(identity=test_farmer.id)

        expense = db.session.query(Expense).filter_by(farmer_id=test_farmer.id).first()
        assert expense is not None

        payload = {
            "amount": 120.0,
            "description": "Updated expense description",
            "category_id": expense.category_id,
            "date": date.today().isoformat(),
            "farmer_id": test_farmer.id
        }

        with app.test_client() as client:
            response = client.put(
                f'/api/expenses/{expense.id}',
                json=payload,
                headers={'Authorization': f'Bearer {access_token}'}
            )

            print(response.data)
            assert response.status_code == 200
            data = response.get_json()
            assert data['amount'] == 120.0
            assert data['description'] == "Updated expense description"
            assert data['date'] == date.today().isoformat()


def test_delete_expense():
    """Test deleting an expense record."""
    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        test_farmer = setup_database(app)
        access_token = create_access_token(identity=test_farmer.id)

        expense = db.session.query(Expense).filter_by(farmer_id=test_farmer.id).first()
        assert expense is not None

        with app.test_client() as client:
            response = client.delete(
                f'/api/expenses/{expense.id}',
                headers={'Authorization': f'Bearer {access_token}'}
            )

            assert response.status_code == 204
            assert db.session.get(Expense, expense.id) is None
