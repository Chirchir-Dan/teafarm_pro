#!/usr/bin/python3
"""Module for class DailySales"""

from sqlalchemy import Column, String, Date, Float, ForeignKey
from models.base_model import BaseModel, db


class DailySales(BaseModel):
    """Representation of a tea sales report"""
    __tablename__ = 'daily_sales'

    grower_id = db.Column(
        db.String(60),
        db.ForeignKey('farmers.id'),
        nullable=False)
    factory = db.Column(db.String(128), nullable=True)
    transaction_id = db.Column(db.String(60), nullable=True)
    plucking_date = db.Column(db.Date, nullable=False)
    total_gross_weight = db.Column(db.Float, nullable=False)
    total_tare_weight = db.Column(db.Float, nullable=False)
    total_net_weight = db.Column(db.Float, nullable=False)

    def __init__(self, *args, **kwargs):
        """Initialization of DailySales"""
        super().__init__(*args, **kwargs)

    def __repr__(self):
        """Return a string representation of the instance."""
        return (
            f"< DailySales(grower_id={self.grower_id}, "
            f"factory={self.factory}, "
            f"transaction_id={self.transaction_id}, "
            f"plucking_date={self.plucking_date}, "
            f"total_gross_weight={self.total_gross_weight}, "
            f"total_tare_weight={self.total_tare_weight}, "
            f"total_net_weight={self.total_net_weight})>"
        )
