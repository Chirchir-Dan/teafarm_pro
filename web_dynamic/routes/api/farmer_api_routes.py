#!/usr/bin/env python3
"""
Routes for Farmer functionalities
"""
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Farmer
from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import create_access_token, jwt_required,
get_jwt_identity

# Blueprint setup
farmer_bp = Blueprint('farmer_bp', __name__, url_prefix='/api/farmers')

# Route 1: Register a new farmer


@farmer_bp.route('/register', methods=['POST'])
def register_farmer():
    """
    Register a new farmer account.
    """
    data = request.get_json()

    # Validate required fields
    if not all(
        field in data for field in [
            'name',
            'phone_number',
            'email',
            'password']):
        abort(
            400,
            description="Missing required fields: name,
            phone_number, email, password")

    # Check if farmer already exists
    if Farmer.query.filter_by(email=data['email']).first():
        abort(400, description="Farmer already exists with this email address")

    # Create a new farmer instance
    farmer = Farmer(
        name=data['name'],
        phone_number=data['phone_number'],
        email=data['email']
    )
    farmer.set_password(data['password'])  # Set the hashed password
    db.session.add(farmer)
    db.session.commit()

    return jsonify(message="Farmer registered successfully"), 201

# Route 2: Farmer login (authenticate and get token)


@farmer_bp.route('/login', methods=['POST'])
def login_farmer():
    """
    Login a farmer and return a JWT token.
    """
    data = request.get_json()

    # Validate required fields
    if 'email' not in data or 'password' not in data:
        abort(400, description="Email and password are required")

    farmer = Farmer.query.filter_by(email=data['email']).first()

    if not farmer or not farmer.check_password(data['password']):
        abort(401, description="Invalid email or password")

    # Create access token
    access_token = create_access_token(identity=farmer.id)
    return jsonify(access_token=access_token), 200

# Route 3: Get farmer's profile details


@farmer_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_farmer_profile():
    """
    Get the current logged-in farmer's profile details.
    """
    farmer_id = get_jwt_identity()
    farmer = Farmer.query.get(farmer_id)

    if not farmer:
        abort(404, description="Farmer not found")

    return jsonify(
        name=farmer.name,
        phone_number=farmer.phone_number,
        email=farmer.email,
        farm_name=farmer.farm_name,
        location=farmer.location,
        total_acreage=farmer.total_acreage
    ), 200

# Route 4: Update farmer's profile details


@farmer_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_farmer_profile():
    """
    Update the current logged-in farmer's profile details.
    """
    farmer_id = get_jwt_identity()
    farmer = Farmer.query.get(farmer_id)

    if not farmer:
        abort(404, description="Farmer not found")

    data = request.get_json()

    if 'name' in data:
        farmer.name = data['name']
    if 'phone_number' in data:
        farmer.phone_number = data['phone_number']
    if 'email' in data:
        farmer.email = data['email']
    if 'farm_name' in data:
        farmer.farm_name = data['farm_name']
    if 'location' in data:
        farmer.location = data['location']
    if 'total_acreage' in data:
        farmer.total_acreage = data['total_acreage']

    db.session.commit()

    return jsonify(message="Profile updated successfully"), 200

# Route 5: Change password for farmer


@farmer_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    """
    Change the password for the current logged-in farmer.
    """
    farmer_id = get_jwt_identity()
    farmer = Farmer.query.get(farmer_id)

    if not farmer:
        abort(404, description="Farmer not found")

    data = request.get_json()

    if 'old_password' not in data or 'new_password' not in data:
        abort(400, description="Old password and new password are required")

    if not farmer.check_password(data['old_password']):
        abort(401, description="Old password is incorrect")

    farmer.set_password(data['new_password'])
    db.session.commit()

    return jsonify(message="Password changed successfully"), 200
