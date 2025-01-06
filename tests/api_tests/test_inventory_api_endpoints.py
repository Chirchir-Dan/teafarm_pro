#!/usr/bin/env python3
import pytest
from web_dynamic.app import create_app, db
from flask_jwt_extended import create_access_token
from models.inventory import Inventory
from models.farmer import Farmer

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
    test_farmer = Farmer(
        name="John Doe",
        email="test@user.com",
        phone_number="123456789",
        password_hash="hashedpassword"
    )
    db.session.add(test_farmer)
    db.session.commit()

    inventory1 = Inventory(
        item_name="Fertilizer",
        quantity=100
    )
    inventory2 = Inventory(
        item_name="Tea Seeds",
        quantity=200
    )
    db.session.add_all([inventory1, inventory2])
    db.session.commit()

    return test_farmer

def test_get_inventory(test_client, setup_data):
    """Test getting all inventory items."""
    test_user = setup_data
    access_token = create_access_token(identity=test_user.id)

    response = test_client.get(
        '/api/inventories',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2

    assert any(item['item_name'] == "Fertilizer" and item['quantity'] == 100 for item in data)
    assert any(item['item_name'] == "Tea Seeds" and item['quantity'] == 200 for item in data)

def test_get_single_inventory_item(test_client, setup_data):
    """Test getting a single inventory item by ID."""
    test_user = setup_data
    access_token = create_access_token(identity=test_user.id)

    inventory_item = Inventory.query.filter_by(item_name="Fertilizer").first()

    response = test_client.get(
        f'/api/inventories/{inventory_item.id}',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['item_name'] == "Fertilizer"
    assert data['quantity'] == 100

def test_create_inventory_item(test_client, setup_data):
    """Test creating a new inventory item."""
    test_user = setup_data
    access_token = create_access_token(identity=test_user.id)

    payload = {
        "item_name": "Pesticide",
        "quantity": 150
    }

    response = test_client.post(
        '/api/inventories',
        json=payload,
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data['item_name'] == "Pesticide"
    assert data['quantity'] == 150

def test_update_inventory_item(test_client, setup_data):
    """Test updating an existing inventory item."""
    test_user = setup_data
    access_token = create_access_token(identity=test_user.id)

    inventory_item = Inventory.query.first()
    payload = {
        "item_name": "Fertilizer",
        "quantity": 120
    }

    response = test_client.put(
        f'/api/inventories/{inventory_item.id}',
        json=payload,
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['item_name'] == "Fertilizer"
    assert data['quantity'] == 120

def test_delete_inventory_item(test_client, setup_data):
    """Test deleting an inventory item."""
    test_user = setup_data
    access_token = create_access_token(identity=test_user.id)

    inventory_item = Inventory.query.first()

    response = test_client.delete(
        f'/api/inventories/{inventory_item.id}',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert response.status_code == 204
    assert db.session.get(Inventory, inventory_item.id) is None
