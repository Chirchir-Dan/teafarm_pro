#!/usr/bin/python3
"""
Contains the class MarketValue
"""

from sqlalchemy import Column, Float, Date
from models.base_model import BaseModel, db


class MarketValue(BaseModel):
    """
    The MarketValue class represents the price per unit weight
    of the produce.
    """
    __tablename__ = 'market_values'

    date = db.Column(db.Date, nullable=False, primary_key=True)
    price_per_kg = db.Column(db.Float, nullable=False)  # Price per kilogram

    def __init__(self, *args, **kwargs):
        """
        Initializes a MarketValue instance
        """
        super().__init__(*args, **kwargs)

    def __repr__(self):
        """Return a string representation of the instance."""
        return f"< MarketValue(date={self.date}, "\
               f"price_per_kg={self.price_per_kg}) >"
