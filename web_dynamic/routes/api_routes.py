from flask import Blueprint, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token,jwt_required,get_jwt, get_jwt_identity
from werkzeug.security import check_password_hash
from werkzeug.exceptions import BadRequest
from models.farmer import Farmer
from sqlalchemy.exc import IntegrityError
from models.employee import Employee
from models.labour import Labour
from models.production import ProductionRecord
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
    required_fields = ['name', 'phone_number', 'password', 'labour_id', 'farmer_id']
    for field in required_fields:
        if not data.get(field):
            raise BadRequest(f"Field '{field}' is required and cannot be empty.")
    
    # Validate farmer_id
    farmer = Farmer.query.get(data['farmer_id'])
    if not farmer:
        raise BadRequest("Invalid farmer_id. Farmer does not exist.")
    
    # Validate labour_id
    job_type = Labour.query.get(data['labour_id'])
    if not job_type:
        raise BadRequest("Invalid labour_id. Job type does not exist.")

    # Check if phone_number is unique
    if Employee.query.filter_by(phone_number=data['phone_number']).first():
        raise BadRequest("Phone number is already in use.")

    # Create and save the new employee
    new_employee = Employee(
        name=data['name'],
        phone_number=data['phone_number'],
        email=data.get('email'),
        labour_id=data['labour_id'],
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
            "labour_id": new_employee.labour_id,
            "farmer_id": new_employee.farmer_id
        }
    }), 201    


@api_bp.route('/employees', methods=['POST'])
@jwt_required()
def create_employee():
    """Route for adding a new employee."""
    try:
        data = request.json
        current_farmer_id = get_jwt_identity()

        # validate required fields
        if not data or not data.get('name') or not data.get('phone_number') or not data.get('password') or not data.get('labour_id'):
            return jsonify({"error": "Fields 'name', 'phone_number', 'password', and 'labour_id' are required."}), 400

        # Check if the job type exists
        job_type = Labour.query.filter_by(id=data['labour_id'], farmer_id=current_farmer_id).first()
        if not job_type:
            return jsonify({"error": "Job type not found."}), 404
        
        # Check if phone number length is not greater than 10
        if len(data['phone_number']) > 10:
            return jsonify({"error": "Phone number must not be more than 10 digits long."}), 400
        
        # Check if the phone number is unique
        if Employee.query.filter_by(name=data['name'], phone_number=data['phone_number'], farmer_id=current_farmer_id).first():
            return jsonify({"error": "Phone number is already in use."}), 409

        new_employee = Employee(
            name=data['name'],
            phone_number=data['phone_number'],
            email=data['email'],
            labour_id=data['labour_id'],
            farmer_id=current_farmer_id
        )
        new_employee.set_password(data['password'])
        db.session.add(new_employee)
        db.session.commit()

        return jsonify({
            "message": "Employee created successfully.",
            "employee": new_employee.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An unexpected error occurred.{e}"}), 500
    

@api_bp.route('/employees/<uuid:employee_id>', methods=['PUT'])
@jwt_required()
def update_employee(employee_id):
    """Route for updating an existing employee."""
    try:
        data = request.json
        current_farmer_id = get_jwt_identity()

        if not data or not data.get('name') or not data.get('phone_number') or not data.get('labour_id'):
            return jsonify({"error": "Fields 'name', 'phone_number', and 'labour_id' are required."}), 400
        
        employee = Employee.query.filter(Employee.id==str(employee_id), Employee.farmer_id==current_farmer_id).first()

        if not employee:
            return jsonify({"error": "Employee not found."}), 404
        
        # Check if the job type exists
        job_type = Labour.query.filter_by(id=data['labour_id'], farmer_id=current_farmer_id).first()
        if not job_type:
            return jsonify({"error": "Job type not found."}), 404
        
        # Check if phone number length is not greater than 10
        if len(data['phone_number']) > 10:
            return jsonify({"error": "Phone number must not be more than 10 digits long."}), 400
        
        # Check if the phone number is unique
        if Employee.query.filter(Employee.phone_number==data['phone_number'], Employee.farmer_id==current_farmer_id, Employee.id!=str(employee_id)).first():
            return jsonify({"error": f"Phone number is already in use. {type(employee_id)}"}), 409
        
        employee.name = data['name']
        employee.phone_number = data['phone_number']
        employee.email = data.get('email', employee.email)
        employee.labour_id = data['labour_id']

        # Update the password if provided
        if data.get('password'):
            employee.set_password(data['password'])

        db.session.commit()

        return jsonify({"message": "Employee updated successfully.", "employee": employee.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An unexpected error occurred. {e}"}), 500


@api_bp.route('/employees', methods=['GET'])
@jwt_required()
def get_employees():
    """Route for fetching all employees of a farmer."""
    try:
        current_farmer_id = get_jwt_identity()
        employees = Employee.query.filter_by(farmer_id=current_farmer_id).all()

        return jsonify({
            "employees": [employee.to_dict() for employee in employees]
        }), 200
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred. {e}"}), 500


@api_bp.route('/employees/<uuid:employee_id>', methods=['DELETE'])
@jwt_required()
def delete_employee(employee_id):
    """Route for deleting an employee."""
    try:
        current_farmer_id = get_jwt_identity()
        employee = Employee.query.filter(Employee.id==str(employee_id), Employee.farmer_id==current_farmer_id).first()

        if not employee:
            return jsonify({"error": "Employee not found."}), 404
        
        db.session.delete(employee)
        db.session.commit()

        return jsonify({"message": "Employee deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An unexpected error occurred.{e}"}), 500


@api_bp.route('/labours', methods=['POST'])
@jwt_required()
def create_labour():
    """Route for creating a new labour type."""
    try:
        data = request.json
        current_farmer_id = get_jwt_identity()

        if not data or not data.get('type') or not data.get('rate'):
            return jsonify({"Fields 'type', 'rate' are required."}), 400
        
        if Labour.query.filter_by(type=data['type'], farmer_id=current_farmer_id).first():
            return jsonify({"error": "Labour type already exists."}), 409

        new_labour = Labour(
            type=data['type'],
            description=data['description'],
            rate=data['rate'],
            farmer_id=current_farmer_id
        )
        db.session.add(new_labour)
        db.session.commit()

        return jsonify({
            "message": "Labour type created successfully.",
            "labour": {"id": new_labour.id, "type": new_labour.to_dict()}
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An unexpected error occurred. {e}"}), 500


@api_bp.route('/labours/<uuid:labour_id>', methods=['PUT'])
@jwt_required()
def update_labour(labour_id):
    """Route for updating an existing labour type."""
    try:
        data = request.json
        current_farmer_id = get_jwt_identity()

        if not data or not data.get('type'):
            return jsonify({"error": "Field 'type' is required."}), 400
        
        labour = Labour.query.filter(Labour.id==str(labour_id), Labour.farmer_id==current_farmer_id).first()

        if not labour:
            return jsonify({"error": f"Labour type not found. {current_farmer_id==labour.farmer_id}"}), 404
    
        # Check if labour type already exists
        if Labour.query.filter(Labour.type == data['type'], Labour.id == labour_id, Labour.farmer_id == current_farmer_id).first():
            return jsonify({"error": "Labour type with this name already exists."}), 409
        
        labour.type = data['type']
        labour.description = data.get('description', labour.description)
        labour.rate = data.get('rate', labour.rate)
        db.session.commit()

        return jsonify({"message": "Labour type updated successfully.", "labour": labour.to_dict()}), 200
    # Handle MySQLdb.IntegrityError
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Labour type with this name already exists."}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An unexpected error occured. {e}"}), 500


@api_bp.route('/labours', methods=['GET'])
@jwt_required()
def get_labours():
    """Route for fetching all labour types."""
    try:
        current_farmer_id = get_jwt_identity()
        labours = Labour.query.filter_by(farmer_id=current_farmer_id).all()

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
        current_farmer_id = get_jwt_identity()
        labour = Labour.query.filter(Labour.id==str(labour_id), Labour.farmer_id==current_farmer_id).first()

        if not labour:
            return jsonify({"error": "Labour type not found."}), 404
    
        db.session.delete(labour)
        db.session.commit()

        return jsonify({"message": "Labour type deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred."}), 500


@api_bp.route('/record_production_data', methods=['POST'])
@jwt_required()
def record_production_data():
    """Route for recording production."""
    try:
        data = request.json
        current_farmer_id = get_jwt_identity()

        if not data or not data.get('weight') or not data.get('employee_id') or not data.get('date'):
            return jsonify({"error": "Fields 'weight', and 'employee' are required."}), 400

        # if rate is not provided, get from employee's job type
        if not data.get('rate'):
            employee = Employee.query.filter_by(id=data['employee_id'], farmer_id=current_farmer_id).first()
            if not employee:
                return jsonify({"error": "Employee not found."}), 404
            data['rate'] = employee.job_type.rate

        new_production = ProductionRecord(
            employee_id=data.get('employee_id'),
            weight=data.get('weight'),
            rate=data.get('rate'),
            date=data.get('date'),
            farmer_id=current_farmer_id
        )

        db.session.add(new_production)
        db.session.commit()

        return jsonify({
            "message": "Production recorded successfully.",
            "production": new_production.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An unexpected error occurred.{e}"}), 500


@api_bp.route('/production_data/<uuid:production_id>', methods=['PUT'])
@jwt_required()
def update_production_data(production_id):
    """Route for updating production data."""
    try:
        data = request.json
        current_farmer_id = get_jwt_identity()

        if not data or not data.get('weight') or not data.get('employee_id') or not data.get('date'):
            return jsonify({"error": "Fields 'weight', 'date' and 'employee' are required."}), 400

        production = ProductionRecord.query.filter(ProductionRecord.id==str(production_id), ProductionRecord.farmer_id==current_farmer_id).first()

        if not production:
            return jsonify({"error": "Production record not found."}), 404

        # if rate is not provided, get from employee's job type
        if not data.get('rate'):
            employee = Employee.query.filter_by(id=data['employee_id'], farmer_id=current_farmer_id).first()
            if not employee:
                return jsonify({"error": "Employee not found."}), 404
            data['rate'] = employee.job_type.rate

        production.employee_id = data['employee_id']
        production.weight = data['weight']
        production.rate = data['rate']
        production.date = data['date']

        db.session.commit()

        return jsonify({
            "message": "Production record updated successfully.",
            "production": production.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An unexpected error occurred. {e}"}), 500


@api_bp.route('/fetch_production_data', methods=['GET'])
@jwt_required()
def fetch_production_data():
    """Route for fetching production data."""
    try:
        current_farmer_id = get_jwt_identity()
        productions = ProductionRecord.query.filter_by(farmer_id=current_farmer_id).all()

        return jsonify({
            "productions": [production.to_dict() for production in productions]
        }), 200
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred. {e}"}), 500


@api_bp.route('/delete_production_data/<uuid:production_id>', methods=['DELETE'])
@jwt_required()
def delete_production_data(production_id):
    """Route for deleting a production record."""
    try:
        current_farmer_id = get_jwt_identity()
        production = ProductionRecord.query.filter(ProductionRecord.id==str(production_id), ProductionRecord.farmer_id==current_farmer_id).first()

        if not production:
            return jsonify({"error": "Production record not found."}), 404

        db.session.delete(production)
        db.session.commit()

        return jsonify({"message": "Production record deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An unexpected error occurred. {e}"}), 500


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