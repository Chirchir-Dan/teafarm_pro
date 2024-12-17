#!/usr/bin/python3
"""
Module for class DailyProductionSummary
"""

from sqlalchemy import Column, Float, Date
from models.base_model import BaseModel, db

class DailyProductionSummary(BaseModel):
    """
    Represents the total production weight for a specific day
    """
    __tablename__ = 'daily_production_summaries'

    date = db.Column(db.Date, nullable=False, unique=True)
    total_weight = db.Column(db.Float, nullable=False, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)

    def __init__(self, *args, **kwargs):
        """
        Initializes a DailyProductionSummary instance
        """
        super().__init__(*args, **kwargs)

    def __repr__(self):
        """Return a string representation of the instance."""
        return (f"<DailyProductionSummary(date={self.date}, total_weight={self.total_weight})>")
