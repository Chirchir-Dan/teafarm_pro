#!/usr/bin/python3
"""
Contains the class Labour
"""

from sqlalchemy import UniqueConstraint
from models.base_model import BaseModel, db


class Labour(BaseModel):
    """
    The Labour class represents the types of labor
    activities and their rates
    """
    __tablename__ = 'labours'

    type = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(128), nullable=True)
    farmer_id = db.Column(db.String(128), db.ForeignKey('farmers.id'), nullable=False)

    # Composite unique constraint
    __table_args__ = (UniqueConstraint('type', 'farmer_id', name='unique_labour_type_per_farmer'), )

    # Relationshhips
    employees = db.relationship('Employee', back_populates='job_type')
    tasks = db.relationship('Task', back_populates='labour')
    farmer = db.relationship('Farmer', back_populates='labours')

    def __init__(self, *args, **kwargs):
        """
        Initializes a Labour instance
        """
        super().__init__(*args, **kwargs)

    def to_dict(self):
        """
        Returns a dictionary representation of the Labour instance
        """
        return {
            'id': self.id,
            'type': self.type,
            'description': self.description,
            'farmer_id': self.farmer_id
        }

    def __repr__(self):
        """
        Returns a string representation of the Labour instance.
        """
        return f" type={self.type})>"
