#!/usr/bin/env python3
"""
Routes for managing Employees under the Farmer
"""
from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Employee, Farmer

# Blueprint setup
employee_bp = Blueprint('employee', __name__, url_prefix='/api/farmers/<farmer_id>/employees')

# Route 1: List employees under a specific farmer
@employee_bp.route('', methods=['GET'])
@jwt_required()
def list_employees(farmer_id):
    """
    Fetch all employees under the farmer's management.
    """
    # Ensure the current user is the correct farmer
    current_farmer_id = get_jwt_identity()
    if current_farmer_id != int(farmer_id):
        abort(403, description="You are not authorized to view employees for this farmer.")

    # Fetch the employees
    farmer = Farmer.query.get(farmer_id)
    if not farmer:
        abort(404, description="Farmer not found.")

    employees = Employee.query.filter_by(farmer_id=farmer.id).all()
    return jsonify([employee.to_dict() for employee in employees]), 200

# Route 2: Add a new employee under a specific farmer
@employee_bp.route('', methods=['POST'])
@jwt_required()
def add_employee(farmer_id):
    """
    Add a new employee under the farmer's management.
    """
    # Ensure the current user is the correct farmer
    current_farmer_id = get_jwt_identity()
    if current_farmer_id != int(farmer_id):
        abort(403, description="You are not authorized to add employees for this farmer.")

    # Validate data
    data = request.get_json()
    if 'name' not in data or 'phone_number' not in data or 'email' not in data or 'job_type' not in data:
        abort(400, description="Missing required fields (name, phone_number, email, job_type).")

    # Add the new employee
    new_employee = Employee(
        name=data['name'],
        phone_number=data['phone_number'],
        email=data['email'],
        job_type=data['job_type'],
        farmer_id=farmer_id  # Associate the employee with the farmer
    )
    
    db.session.add(new_employee)
    db.session.commit()

    return jsonify(new_employee.to_dict()), 201

# Route 3: Remove an employee under a specific farmer
@employee_bp.route('', methods=['DELETE'])
@jwt_required()
def remove_employee(farmer_id):
    """
    Remove an employee under the farmer's management.
    """
    # Ensure the current user is the correct farmer
    current_farmer_id = get_jwt_identity()
    if current_farmer_id != int(farmer_id):
        abort(403, description="You are not authorized to remove employees for this farmer.")

    # Validate data
    data = request.get_json()
    if 'employee_id' not in data:
        abort(400, description="Missing required field (employee_id).")

    # Find the employee
    employee = Employee.query.get(data['employee_id'])
    if not employee or employee.farmer_id != farmer_id:
        abort(404, description="Employee not found or not managed by this farmer.")

    # Remove the employee
    db.session.delete(employee)
    db.session.commit()

    return jsonify(message="Employee removed successfully"), 200
