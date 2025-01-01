from flask import Blueprint, request, jsonify
from flask_jwt_extended import JWTManager,\
    create_access_token, jwt_required, get_jwt
from werkzeug.security import check_password_hash
from werkzeug.exceptions import BadRequest
from models.farmer import Farmer
from models.employee import Employee
from models.labour import Labour
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
        return jsonify({"error": "Name, email, phone number,\
                and password are required"}), 400

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
        refresh_token = create_refresh_token(identity=str(user.id))
        username = user.name
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'username': username
            }), 200
    else:
        return jsonify({'error': 'Invalid email or password'}), 401
    

@api_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Route for refreshing an expired JWT token.
    """
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return jsonify({'access_token': access_token}), 200

def create_employee():
    """Create a new employee for a specific farmer."""
    data = request.json
    required_fields = ['name', 'phone_number', 'password', 'job_type_id', 'farmer_id']
    for field in required_fields:
        if not data.get(field):
            raise BadRequest(f"Field '{field}' is required and cannot be empty.")
    
    # Validate farmer_id
    farmer = Farmer.query.get(data['farmer_id'])
    if not farmer:
        raise BadRequest("Invalid farmer_id. Farmer does not exist.")
    
    # Validate job_type_id
    job_type = Labour.query.get(data['job_type_id'])
    if not job_type:
        raise BadRequest("Invalid job_type_id. Job type does not exist.")

    # Check if phone_number is unique
    if Employee.query.filter_by(phone_number=data['phone_number']).first():
        raise BadRequest("Phone number is already in use.")

    # Create and save the new employee
    new_employee = Employee(
        name=data['name'],
        phone_number=data['phone_number'],
        email=data.get('email'),
        job_type_id=data['job_type_id'],
        farmer_id=data['farmer_id']
    )
    new_employee.set_password(data['password'])  # Hash the password before saving
    new_employee.save()

    return jsonify({
        "message": "Employee created successfully.",
        "employee": {
            "id": new_employee.id,
            "name": new_employee.name,
            "phone_number": new_employee.phone_number,
            "email": new_employee.email,
            "job_type_id": new_employee.job_type_id,
            "farmer_id": new_employee.farmer_id
        }
    }), 201    


@api_bp.route('/employees', methods=['POST'])
@jwt_required()
def add_employee():
    """Route for adding a new employee."""
    try:
        data = request.json
        return create_employee(data)
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred."}), 500
    

@api_bp.route('/labours', methods=['POST'])
@jwt_required()
def create_labour():
    """Route for creating a new labour type."""
    try:
        data = request.json
        if not data or not data.get('type'):
            return jsonify({"Field 'type' is required."}), 400
        
        if Labour.query.filter_by(type=data['type']).first():
            return jsonify({"error": "Labour type already exists."}), 409
        
        new_labour = Labour(type=data['type'], description=data.get('description'))
        db.session.add(new_labour)
        db.session.commit()

        return jsonify({
            "message": "Labour type created successfully.",
            "labour": {"id": new_labour.id, "type": new_labour.to_dict()}
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred."}), 500


@api_bp.route('/labours/<uuid:labour_id>', methods=['PUT'])
@jwt_required()
def update_labour(labour_id):
    """Route for updating an existing labour type."""
    try:
        data = request.json

        if not data or not data.get('type'):
            return jsonify({"error": "Field 'type' is required."}), 400
        
        labour = Labour.query.get(labour_id)

        if not labour:
            return jsonify({"error": "Labour type not found."}), 404
    
        # Check if labour type already exists
        if Labour.query.filter(Labour.type == data['type'], Labour.id == labour_id).first():
            return jsonify({"error": "Labour type with this name already exists."}), 409
        
        labour.type = data['type']
        labour.description = data.get('description', labour.description)
        db.session.commit()

        return jsonify({"message": "Labour type updated successfully.", "labour": labour.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An unexpected error occured."}), 500


@api_bp.route('/labours', methods=['GET'])
@jwt_required()
def get_labours():
    """Route for fetching all labour types."""
    try:
        labours = Labour.query.all()
        return jsonify({
            "labours": [labour.to_dict() for labour in labours]
        }), 200
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred."}), 500


@api_bp.route('/labours/<uuid:labour_id>', methods=['DELETE'])
@jwt_required()
def delete_labour(labour_id):
    """Route for deleting a labour type."""
    try:
        labour = Labour.query.get(labour_id)
        if not labour:
            return jsonify({"error": "Labour type not found."}), 404
    
        db.session.delete(labour)
        db.session.commit()

        return jsonify({"message": "Labour type deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred."}), 500


@api_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout route for invalidating the current JWT token.
    """
    try:
        from web_dynamic.app import BLACKLIST
        jti = get_jwt()['jti']
        BLACKLIST.add(jti)
        return jsonify({'message': 'Successfully logged out'}), 200
    # handle 401 error
    except KeyError:
        return jsonify({'message': 'Token is missing'}), 401
    except Exception as e:
        return jsonify({'error': f'An error occured: {str(e)}'}), 500
