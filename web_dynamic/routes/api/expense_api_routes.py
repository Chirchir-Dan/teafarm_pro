#!/usr/bin/env python3
"""
Expense API routes for managing expenses in the application.

This module contains the API endpoints for CRUD operations related to
expenses, including creating, reading, updating, and deleting expenses.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models.expense import Expense
from models import db
import traceback
from datetime import date

# Initialize Blueprint
expense_bp = Blueprint('expense_bp', __name__)

@expense_bp.route('/expenses', methods=['GET'])
@jwt_required()
def get_expenses():
    """
    Retrieve a list of all expenses.

    Returns:
        JSON: A list of expense records or an error message.
    """
    try:
        expenses = Expense.query.all()
        result = [expense.to_dict() for expense in expenses]
        return jsonify(result), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch expenses: {str(e)}"}), 500


@expense_bp.route('/expenses/<id>', methods=['GET'])
@jwt_required()
def get_expense(id):
    """
    Retrieve details of a specific expense.

    Args:
        id (int): The ID of the expense to retrieve.

    Returns:
        JSON: The expense details or an error message.
    """
    try:
        expense = db.session.get(Expense, id)
        if not expense:
            return jsonify({"error": "Expense not found"}), 404
        return jsonify(expense.to_dict()), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch expense: {str(e)}"}), 500


@expense_bp.route('/expenses', methods=['POST'])
@jwt_required()
def create_expense():
    """
    Add a new expense record.

    Request JSON:
        {
            "category_id": "<category_id>",
            "description": "<description>",  # Nullable field
            "amount": <amount>,
            "farmer_id": <farmer_id>
            "date": <date>
        }

    Returns:
        JSON: The newly created expense record or an error message.
    """
    data = request.get_json()
    category_id = data.get('category_id')
    description = data.get('description', None)  # Default to None if not provided
    amount = data.get('amount')
    farmer_id = data.get('farmer_id')

    if not all([category_id, amount, farmer_id]):
        return jsonify({"error": "Category ID, amount, and farmer ID are required"}), 400

    try:
        new_expense = Expense(
            category_id=category_id,
            description=description,
            amount=amount,
            farmer_id=farmer_id,
            date=date
        )
        db.session.add(new_expense)
        db.session.commit()
        return jsonify(new_expense.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create expense: {str(e)}"}), 500


@expense_bp.route('/expenses/<id>', methods=['PUT'])
@jwt_required()
def update_expense(id):
    """
    Update an existing expense record.

    Args:
        id (int): The ID of the expense to update.

    Request JSON:
        {
            "category_id": "<category_id>",
            "description": "<description>",  # Nullable field
            "amount": <amount>,
            "farmer_id": <farmer_id>
        }

    Returns:
        JSON: The updated expense record or an error message.
    """
    data = request.get_json()
    category_id = data.get('category_id')
    description = data.get('description', None)  # Default to None if not provided
    amount = data.get('amount')
    farmer_id = data.get('farmer_id')

    if not all([category_id, amount, farmer_id]):
        return jsonify({"error": "Category ID, amount, and farmer ID are required"}), 400

    try:
        expense = db.session.get(Expense, id)
        if not expense:
            return jsonify({"error": "Expense not found"}), 404

        expense.category_id = category_id
        expense.description = description
        expense.amount = amount
        expense.farmer_id = farmer_id
        db.session.commit()

        return jsonify(expense.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update expense: {str(e)}"}), 500


@expense_bp.route('/expenses/<id>', methods=['DELETE'])
@jwt_required()
def delete_expense(id):
    """
    Delete a specific expense record.

    Args:
        id (int): The ID of the expense to delete.

    Returns:
        JSON: A success message or an error message.
    """
    try:
        expense = db.session.get(Expense, id)
        if not expense:
            return jsonify({"error": "Expense not found"}), 404

        db.session.delete(expense)
        db.session.commit()

        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete expense: {str(e)}"}), 500
