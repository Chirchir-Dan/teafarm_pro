#!/usr/bin/python3
"""
Defines the Expense model
"""

from datetime import datetime
import enum
from sqlalchemy import Float, String, DateTime, Enum
from models.base_model import BaseModel, db


class Expense(BaseModel):
    """Represents an expense incurred by the farm."""
    __tablename__ = 'expenses'

    category_id = db.Column(
        db.String(128),
        db.ForeignKey('labours.id'),
        nullable=False)
    description = db.Column(db.String(255), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)

    # Relationship with Labour model
    category = db.relationship('Labour', backref='expenses')

    def __init__(self, *args, **kwargs):
        """
        Initializes an Expense instance.
        """
        super().__init__(*args, **kwargs)

    def __repr__(self):
        """Return a string representation of the instance."""
        return (f"<Expense(id={self.id}, amount={self.amount}, "
                f"description={self.description}, date={self.date}, "
                f"category={self.category})>")

    def to_dict(self):
        """Convert the Expense instance to a dictionary."""
        return {
            "id": self.id,
            "category_id": self.category_id,
            "description": self.description,
            "amount": self.amount,
            "date": self.date.isoformat() if self.date else None,
            "category": self.category.to_dict() if self.category else None
        }
