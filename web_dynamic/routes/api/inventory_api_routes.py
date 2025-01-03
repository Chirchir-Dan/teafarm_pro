#!/usr/bin/env python3
"""
This module contains the API routes for managing inventory in the TeaFarm Pro application.
"""

from flask import Blueprint, request, jsonify, abort
from models import db
from models.inventory import Inventory
from flask_jwt_extended import jwt_required

# Create a Blueprint for the inventory API routes
inventory_bp = Blueprint('inventory_bp', __name__)

# Route to create a new inventory item
@inventory_bp.route('/inventories', methods=['POST'])
@jwt_required()
def create_inventory():
    """
    Create a new inventory item.
    """
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('item_name') or \
            not isinstance(data.get('quantity'), (int, float)):
        abort(400, description="Item name and valid quantity are required")
    
    # Create the inventory item
    item_name = data['item_name']
    quantity = data['quantity']
    new_inventory = Inventory(item_name=item_name, quantity=quantity)
    
    # Add to the session and commit
    db.session.add(new_inventory)
    db.session.commit()
    
    return jsonify(new_inventory.to_dict()), 201


# Route to get all inventory items
@inventory_bp.route('/inventories', methods=['GET'])
@jwt_required()
def get_all_inventories():
    """
    Get all inventory items.
    """
    inventories = Inventory.query.all()
    
    return jsonify([inventory.to_dict() for inventory in inventories]), 200


# Route to get a specific inventory item by ID
@inventory_bp.route('/inventories/<id>', methods=['GET'])
@jwt_required()
def get_inventory(id):
    """
    Get a specific inventory item by its ID.
    """
    inventory = db.session.get(Inventory, id)
    
    if not inventory:
        abort(404, description="Inventory item not found")
    
    return jsonify(inventory.to_dict()), 200


# Route to update an inventory item's quantity
@inventory_bp.route('/inventories/<id>', methods=['PUT'])
@jwt_required()
def update_inventory(id):
    """
    Update the quantity of an inventory item.
    """
    inventory = db.session.get(Inventory, id)
    
    if not inventory:
        abort(404, description="Inventory item not found")
    
    data = request.get_json()
    
    # Validate and update quantity if provided
    if 'quantity' in data:
        if not isinstance(data['quantity'], (int, float)):
            abort(400, description="A valid quantity is required")
        inventory.update_quantity(float(data['quantity']))
    
    # Validate and update item_name if provided
    if 'item_name' in data:
        if not isinstance(data['item_name'], str):
            abort(400, description="A valid item name is required")
        inventory.item_name = data['item_name']

    db.session.commit()

    return jsonify(inventory.to_dict()), 200


# Route to delete an inventory item
@inventory_bp.route('/inventories/<id>', methods=['DELETE'])
@jwt_required()
def delete_inventory(id):
    """
    Delete an inventory item.
    """
    inventory = db.session.get(Inventory, id)
    
    if not inventory:
        abort(404, description="Inventory item not found")
    
    db.session.delete(inventory)
    db.session.commit()
    
    return jsonify({"message": "Inventory item deleted successfully"}), 204
