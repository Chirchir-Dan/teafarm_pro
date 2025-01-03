#!/usr/bin/env python3
"""
This module contains the Inventory model for tracking inventory
in the TeaFarm Pro application.
"""

from datetime import datetime
from models.base_model import BaseModel, db


class Inventory(BaseModel):
    """
    Model for tracking inventory in the TeaFarm Pro application.

    Attributes:
        id (int): Primary key of the inventory item.
        item_name (str): Name of the inventory item.
        quantity (float): Quantity of the inventory item.
        date_added (datetime): Timestamp when inventory was added.
        date_updated (datetime): Timestamp of when the inventory
        was last updated.
    """
    __tablename__ = 'inventories'

    item_name = db.Column(db.String(255), nullable=False)
    # Changed to Float for decimal values
    quantity = db.Column(db.Float, nullable=False, default=0)
    date_added = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False)

    def __repr__(self):
        """
        Return a string representation of the Inventory instance.

        Returns:
            str: A string representing the Inventory instance.
        """
        return f'<Inventory {self.item_name} - {self.quantity} units>'

    def update_quantity(self, amount):
        """
        Update the quantity of the inventory item.

        Args:
            amount (float): The amount to adjust the quantity by.
        """
        self.quantity = amount
        self.date_updated = datetime.utcnow()
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'item_name': self.item_name,
            'quantity': self.quantity,
            'date_added': self.date_added.isoformat()
        }


