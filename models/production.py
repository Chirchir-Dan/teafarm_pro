#!/usr/bin/python3
"""
Module for class ProductionRecord
"""

from sqlalchemy import Column, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from models.base_model import BaseModel, db

class ProductionRecord(BaseModel):
    """
    Represents the output from production activities by an employee
    """
    __tablename__ = 'productions'

    employee_id = db.Column(db.String(128), db.ForeignKey('employees.id'), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    rate = db.Column(db.Float, nullable=False)  # Rate per kg recorded at the time of production
    date = db.Column(db.Date, nullable=False)

    # Relationship with the Employee model
    employee = relationship('Employee', back_populates='productions')

    def __init__(self, *args, **kwargs):
        """
        Initializes a ProductionRecord instance
        """
        super().__init__(*args, **kwargs)

    @property
    def amount_paid(self):
        """
        Calculate amount paid based on weight and rate
        """
        return self.weight * self.rate

    def __repr__(self):
        """Return a string representation of the instance."""
        return (f"<ProductionRecord(employee_id={self.employee_id}, weight={self.weight}, "
                f"rate={self.rate}, date={self.date}, amount_paid={self.amount_paid})>")
