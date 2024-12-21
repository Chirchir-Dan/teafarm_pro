#!/usr/bin/python3
"""
Contains the class PluckingRate
"""

from sqlalchemy import Column, Float, Date
from models.base_model import BaseModel, db

class PluckingRate(BaseModel):
    """
    The PluckingRate class represents the payment rate per kilogram 
    of tea leaves plucked. This rate is uniform for all employees.
    """
    __tablename__ = 'plucking_rates'

    date = db.Column(Date, nullable=False, primary_key=True)  # Date when rate was set
    rate_per_kg = db.Column(Float, nullable=False)  # Rate per kilogram

    def __init__(self, *args, **kwargs):
        """
        Initializes a PluckingRate instance
        """
        super().__init__(*args, **kwargs)

    def __repr__(self):
        """Return a string representation of the instance."""
        return f"<PluckingRate(date={self.date}, rate_per_kg={self.rate_per_kg})>"
