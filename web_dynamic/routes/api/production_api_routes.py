#!/usr/bin/env python3
"""
Production API routes for managing production records in the application.

This module contains the API endpoints for CRUD operations related to
production records, including creating, reading, updating, and deleting
production records, as well as retrieving production summaries by employee
and calculating total production within a specified date range.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models.production import ProductionRecord  # Correct model import
from models import db

# Initialize Blueprint
api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/productions', methods=['GET'])
@jwt_required()
def get_productions():
    """
    Retrieve a list of all production records.

    Returns:
        JSON: A list of production records or an error message.
    """
    try:
        productions = ProductionRecord.query.all()
        result = [production.to_dict() for production in productions]
        return jsonify(result), 200
    except Exception as e:
        return jsonify(
            {"error": f"Failed to fetch productions: {str(e)}"}
        ), 500


@api_bp.route('/productions/<id>', methods=['GET'])
@jwt_required()
def get_production(id):
    """
    Retrieve details of a specific production record.

    Args:
        id (int): The ID of the production record to retrieve.

    Returns:
        JSON: The production record details or an error message.
    """
    try:
        production = db.session.get(ProductionRecord, id)
        if not production:
            return jsonify({"error": "Production record not found"}), 404
        return jsonify(production.to_dict()), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch production: {str(e)}"}), 500


@api_bp.route('/productions', methods=['POST'])
@jwt_required()
def create_production():
    """
    Add a new production record.

    Request JSON:
        {
            "date": "<date>",
            "weight": <weight>,
            "rate": <rate>,
            "employee_id": <employee_id>
        }

    Returns:
        JSON: The newly created production record or an error message.
    """
    data = request.get_json()
    date = data.get('date')
    weight = data.get('weight')
    rate = data.get('rate')
    employee_id = data.get('employee_id')

    if not all([date, weight, rate, employee_id]):
        return jsonify(
            {"error": "Date, weight, rate, and employee_id are required"}
        ), 400

    try:
        new_production = ProductionRecord(
            date=date, weight=weight, rate=rate, employee_id=employee_id
        )
        db.session.add(new_production)
        db.session.commit()
        return jsonify(new_production.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(
            {"error": f"Failed to create production: {str(e)}"}
        ), 500


@api_bp.route('/productions/<id>', methods=['PUT'])
@jwt_required()
def update_production(id):
    """
    Update an existing production record.

    Args:
        id (int): The ID of the production record to update.

    Request JSON:
        {
            "date": "<date>",
            "weight": <weight>,
            "rate": <rate>,
            "employee_id": <employee_id>
        }

    Returns:
        JSON: The updated production record or an error message.
    """
    data = request.get_json()
    date = data.get('date')
    weight = data.get('weight')
    rate = data.get('rate')
    employee_id = data.get('employee_id')

    if not all([date, weight, rate, employee_id]):
        return jsonify(
            {"error": "Date, weight, rate, and employee_id are required"}
        ), 400

    try:
        production = db.session.get(ProductionRecord, id)
        if not production:
            return jsonify(
                {"error": "Production record not found"}
            ), 404

        production.date = date
        production.weight = weight
        production.rate = rate
        production.employee_id = employee_id
        db.session.commit()

        return jsonify(production.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(
            {"error": f"Failed to update production: {str(e)}"}
        ), 500


@api_bp.route('/productions/<id>', methods=['DELETE'])
@jwt_required()
def delete_production(id):
    """
    Delete a specific production record.

    Args:
        id (int): The ID of the production record to delete.

    Returns:
        JSON: A success message or an error message.
    """
    try:
        production = db.session.get(ProductionRecord, id)
        if not production:
            return jsonify(
                {"error": "Production record not found"}
            ), 404

        db.session.delete(production)
        db.session.commit()

        return '', 204

    except Exception as e:
        db.session.rollback()
        return jsonify(
            {"error": f"Failed to delete production: {str(e)}"}
        ), 500


@api_bp.route('/productions/employee/<employee_id>', methods=['GET'])
@jwt_required()
def get_productions_by_employee(employee_id):
    """
    Retrieve all production records for a specific employee.

    Args:
        employee_id (int): The ID of the employee.

    Returns:
        JSON: A list of production records for the employee or an error
              message.
    """
    try:
        productions = ProductionRecord.query.filter_by(employee_id=employee_id).all()
        if not productions:
            return jsonify(
                {"error": "No productions found for this employee"}), 404

        result = [production.to_dict() for production in productions]
        return jsonify(result), 200
    except Exception as e:
        return jsonify(
            {"error": f"Failed to fetch productions for employee: {str(e)}"}
        ), 500


@api_bp.route('/productions/total', methods=['GET'])
@jwt_required()
def get_total_production():
    """
    Calculate the total production within a given date range.

    Request JSON:
        {
            "start_date": "<start_date>",
            "end_date": "<end_date>"
        }

    Returns:
        JSON: Total production quantity for the given date range.
    """
    data = request.get_json()
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not start_date or not end_date:
        return jsonify(
            {"error": "Start date and end date are required"}
        ), 400

    try:
        total_production = ProductionRecord.query.filter(
            ProductionRecord.date >= start_date,
            ProductionRecord.date <= end_date
        ).with_entities(db.func.sum(ProductionRecord.weight)).scalar()

        return jsonify({"total_production": total_production}), 200
    except Exception as e:
        return jsonify(
            {"error": f"Failed to calculate total production: {str(e)}"}
        ), 500
