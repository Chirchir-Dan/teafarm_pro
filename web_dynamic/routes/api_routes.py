from flask import Blueprint, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt
from werkzeug.security import check_password_hash
from models.farmer import Farmer
from models import db

# Initialize Blueprint
api_bp = Blueprint('api_bp', __name__)

# JWTManager must be initialized in app.py
jwt = JWTManager()

@api_bp.route('/register', methods=['POST'])
def register():
    """
    Endpoint for Farmer registration
    """
    data = request.json
    name = data.get('name')
    email = data.get('email')
    phone_number = data.get('phone_number')
    password = data.get('password')
    farm_name = data.get('farm_name', '')  # Optional
    location = data.get('location', '')    # Optional
    total_acreage = data.get('total_acreage', 0)  # Optional, default to 0

    # Validate required fields
    if not all([name, email, phone_number, password]):
        return jsonify({"error": "Name, email, phone number, and password are required"}), 400

    # Check for existing email or phone number
    if Farmer.query.filter((Farmer.email == email) | (Farmer.phone_number == phone_number)).first():
        return jsonify({"error": "Farmer with this email or phone number already exists"}), 409

    # Create new Farmer instance
    new_farmer = Farmer(
        name=name,
        email=email,
        phone_number=phone_number,
        farm_name=farm_name,
        location=location,
        total_acreage=total_acreage
    )
    new_farmer.set_password(password)

    try:
        db.session.add(new_farmer)
        db.session.commit()
        return jsonify({"message": "Farmer registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to register farmer: {str(e)}"}), 500

@api_bp.route('/login', methods=['POST'])
def login():
    """
    Login route for authenticating users and returning a JWT token.
    """
    data = request.get_json()

    # Check if email and password are provided
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    email = data.get('email')
    password = data.get('password')

    # Look up the Farmer
    user = Farmer.query.filter_by(email=email).first()

    if user and check_password_hash(user.password_hash, password):
        # Create a JWT token
        access_token = create_access_token(identity=str(user.id)) # set sub to user.id as a string
        return jsonify({'message': 'Login successful', 'access_token': access_token}), 200
    else:
        return jsonify({'error': 'Invalid email or password'}), 401


@api_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout route for invalidating the current JWT token.
    """
    from web_dynamic.app import BLACKLIST
    jti = get_jwt()['jti']
    BLACKLIST.add(jti)
    return jsonify({'message': 'Successfully logged out'}), 200