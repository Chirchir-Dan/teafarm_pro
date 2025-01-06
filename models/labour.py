#!/usr/bin/python3
"""
Contains the class Labour
"""

from sqlalchemy import Enum, Numeric
from models.base_model import BaseModel, db


class Labour(BaseModel):
    """
    The Labour class represents the types of labor
    activities and their rates
    """
    __tablename__ = 'labours'

    type = db.Column(db.String(128), nullable=False, unique=True)
    farmer_id = db.Column(db.String(36), db.ForeignKey('farmers.id'), nullable=False)

    # Relationshhips
    farmer = db.relationship('Farmer', back_populates='labours')
    employees = db.relationship('Employee', back_populates='job_type')

    def __init__(self, *args, **kwargs):
        """
        Initializes a Labour instance
        """
        super().__init__(*args, **kwargs)

    def __repr__(self):
        """
        Returns a string representation of the Labour instance.
        """
        return f"<Labour(type={self.type})>"

    def to_dict(self):
        """
        Returns a dictionary representation of the labour instance
        """
        return {
            "id": self.id,
            "type": self.type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
