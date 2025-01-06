#!/usr/bin/env python3
import pytest
import uuid
from web_dynamic.app import create_app, db
from models.production import ProductionRecord
from flask_jwt_extended import create_access_token
from models.employee import Employee
from models.farmer import Farmer
from models.labour import Labour


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
        farmer_id=test_farmer.id)
    db.session.add(labour_type)
    db.session.commit()


    test_user = Employee(
        name="Test Employee",
        email="test@employee.com",
        phone_number="1234567890",
        job_type_id=labour_type.id,
        password_hash="password",
        farmer_id=test_farmer.id
    )
    db.session.add(test_user)
    db.session.commit()

    production = ProductionRecord(
        id=uuid.uuid4(),  # Generate UUID for id
        employee_id=test_user.id,
        weight=100.0,
        rate=10.0,
        date="2024-12-01",
        farmer_id=test_farmer.id
    )
    db.session.add(production)
    db.session.commit()

    print(f"Test Farmer ID: {test_farmer.id}")
    print(f"Test User ID: {test_user.id}")
    print(f"Production Farmer ID: {production.farmer_id}")


    return test_user, test_farmer, production


def test_get_productions():
    """Test getting all production records."""
    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        test_user, test_farmer, production = setup_database(app)

        access_token = create_access_token(identity=test_user.id)

        with app.test_client() as client:
            response = client.get(
                '/api/productions',
                headers={'Authorization': f'Bearer {access_token}'}
            )

            assert response.status_code == 200
            data = response.get_json()
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]['date'] == "2024-12-01"
            assert data[0]['weight'] == 100.0
            assert data[0]['rate'] == 10.0


def test_get_single_production():
    """Test getting a single production record by ID."""
    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        test_user, test_farmer, production = setup_database(app)
        access_token = create_access_token(identity=test_user.id)

        production = ProductionRecord.query.first()

        with app.test_client() as client:
            response = client.get(
                f'/api/productions/{production.id}',
                headers={'Authorization': f'Bearer {access_token}'}
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data['date'] == "2024-12-01"
            assert data['weight'] == 100.0
            assert data['rate'] == 10.0


def test_create_production():
    """Test creating a new production record."""
    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        test_user, test_farmer, production = setup_database(app)
        access_token = create_access_token(identity=test_user.id)

        payload = {
            "employee_id": test_user.id,
            "weight": 150.0,
            "rate": 12.0,
            "date": "2024-12-02",
            "farmer_id": test_farmer.id
        }

        with app.test_client() as client:
            response = client.post(
                '/api/productions',
                json=payload,
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            print(response.data)
            assert response.status_code == 201
            data = response.get_json()
            assert data['weight'] == 150.0
            assert data['rate'] == 12.0


def test_update_production():
    """Test updating an existing production record."""
    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        test_user, test_farmer, production = setup_database(app)
        access_token = create_access_token(identity=test_user.id)

        production = ProductionRecord.query.first()
        payload = {
            "date":"2024-12-01",
            "weight": 120.0,
            "rate": 11.0,
            "employee_id": production.employee_id
        }

        with app.test_client() as client:
            response = client.put(
                f'/api/productions/{production.id}',
                json=payload,
                headers={'Authorization': f'Bearer {access_token}'}
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data['weight'] == 120.0
            assert data['rate'] == 11.0


def test_delete_production():
    """Test deleting a production record."""
    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        test_user, test_farmer, production = setup_database(app)
        access_token = create_access_token(identity=test_user.id)

        production = ProductionRecord.query.first()

        with app.test_client() as client:
            response = client.delete(
                f'/api/productions/{production.id}',
                headers={'Authorization': f'Bearer {access_token}'}
            )

            assert response.status_code == 204
            assert db.session.get(ProductionRecord, production.id) is None


def test_total_production():
    """Test calculating total production within a date range."""
    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        test_user, test_farmer, production = setup_database(app)
        access_token = create_access_token(identity=test_user.id)

        payload = {
            "start_date": "2024-12-01",
            "end_date": "2024-12-31"
        }

        with app.test_client() as client:
            response = client.get(
                '/api/productions/total',
                json=payload,
                headers={'Authorization': f'Bearer {access_token}'}
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data['total_production'] == 100.0
