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

    # Relationshhips
    employees = db.relationship('Employee', back_populates='job_type')
    tasks = db.relationship('Task', back_populates='labour')

    def __init__(self, *args, **kwargs):
        """
        Initializes a Labour instance
        """
        super().__init__(*args, **kwargs)

    def __repr__(self):
        """
        Returns a string representation of the Labour instance.
        """
        return f" type={self.type})>"
