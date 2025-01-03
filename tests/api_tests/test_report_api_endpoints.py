#!/usr/bin/env python3
import pytest
from web_dynamic.app import create_app, db
from flask_jwt_extended import create_access_token
from models.expense import Expense
from models.farmer import Farmer
from models.labour import Labour  # Ensure Labour model is imported

@pytest.fixture(scope='function')
def test_app():
    """Fixture to create and configure a new app instance for each test."""
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def test_client(test_app):
    """Fixture to provide a test client for each test."""
    return test_app.test_client()

@pytest.fixture(scope='function')
def setup_data():
    """Fixture to set up initial data in the database."""
    # Create a Labour category
    labour = Labour(
        type="Plucking",  # or another type from your Labour enum
        rate=10.0  # Example rate
    )
    db.session.add(labour)
    db.session.commit()

    # Create a Farmer
    test_farmer = Farmer(
        name="John Doe",
        email="test@user.com",
        phone_number="123456789",
        password_hash="hashedpassword"
    )
    db.session.add(test_farmer)
    db.session.commit()

    # Create an Expense related to the Labour category
    expense = Expense(
        category_id=labour.id,  # Use the Labour category's ID
        description="Fertilizer cost",
        amount=50.0,
        date="2025-01-01"
    )
    db.session.add(expense)
    db.session.commit()

    return test_farmer, labour  # Return both farmer and labour for use in tests

def test_get_expenses(test_client, setup_data):
    """Test getting all expenses."""
    test_farmer, labour = setup_data
    access_token = create_access_token(identity=test_farmer.id)

    response = test_client.get(
        '/api/expenses',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Check that the expense has the correct category_id
    assert any(item['category_id'] == str(labour.id) for item in data)

def test_get_single_expense(test_client, setup_data):
    """Test getting a single expense by ID."""
    test_farmer, labour = setup_data
    access_token = create_access_token(identity=test_farmer.id)

    expense = Expense.query.filter_by(category_id=labour.id).first()

    response = test_client.get(
        f'/api/expenses/{expense.id}',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['category_id'] == str(labour.id)
    assert data['amount'] == 50.0

def test_create_expense(test_client, setup_data):
    """Test creating a new expense."""
    test_farmer, labour = setup_data
    access_token = create_access_token(identity=test_farmer.id)

    payload = {
        "category_id": labour.id,  # Valid category ID
        "description": "Pesticide cost",
        "amount": 150.0,
        "date": "2025-02-01"
    }

    response = test_client.post(
        '/api/expenses',
        json=payload,
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data['category_id'] == str(labour.id)
    assert data['description'] == "Pesticide cost"
    assert data['amount'] == 150.0

def test_update_expense(test_client, setup_data):
    """Test updating an existing expense."""
    test_farmer, labour = setup_data
    access_token = create_access_token(identity=test_farmer.id)

    expense = Expense.query.filter_by(category_id=labour.id).first()
    payload = {
        "category_id": labour.id,
        "description": "Updated expense",
        "amount": 200.0,
        "date": "2025-03-01"
    }

    response = test_client.put(
        f'/api/expenses/{expense.id}',
        json=payload,
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['category_id'] == str(labour.id)
    assert data['description'] == "Updated expense"
    assert data['amount'] == 200.0

def test_delete_expense(test_client, setup_data):
    """Test deleting an expense."""
    test_farmer, labour = setup_data
    access_token = create_access_token(identity=test_farmer.id)

    expense = Expense.query.filter_by(category_id=labour.id).first()

    response = test_client.delete(
        f'/api/expenses/{expense.id}',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert response.status_code == 204
    assert db.session.get(Expense, expense.id) is None
