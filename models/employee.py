#!/usr/bin/python3
"""
Defines the Employee model
"""

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from models.base_model import BaseModel, db
from sqlalchemy import Enum
from sqlalchemy.orm import relationship
from models.labour import Labour
from models.production import ProductionRecord
from models.production import ProductionRecord


class Employee(BaseModel, UserMixin):
    """
    Represents an employee in the farm
    """
    __tablename__ = 'employees'

    name = db.Column(db.String(128), nullable=False)
    phone_number = db.Column(db.String(10), nullable=False, unique=True)
    email = db.Column(db.String(128), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    farmer_id = db.Column(db.String(128), db.ForeignKey('farmers.id'), nullable=False)
    job_type_id = db.Column(db.String(128), db.ForeignKey('labours.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)


    # Relationships
    productions = db.relationship(
        'ProductionRecord',
        back_populates='employee'
    )
    job_type = db.relationship('Labour', back_populates='employees')
    farmer = db.relationship('Farmer', back_populates='employees')

    def __init__(self, *args, **kwargs):
        """
        Initializes a new Employee instance.
        """
        super().__init__(*args, **kwargs)

    def set_password(self, password):
        """Hashes the password and stores it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks the password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    @classmethod
    def get_employees(cls):
        """Method to retrieve all employees"""
        return cls.query.all()

    @classmethod
    def get_active_employees(cls):
        """
        Retrieves all active employees.
        
        :return: List of active Employee instances.
        """
        return cls.query.filter_by(is_active=True).all()

    @property
    def is_farmer(self):
        return False

    @property
    def is_employee(self):
        return True

    def __repr__(self):
        """Return a string representation of the instance."""
        return (
            f"< Employee(name={self.name}, id={self.id}, "
            f"job_type={self.job_type.type if self.job_type else 'N/A'}, "
            f"is_active={self.is_active})>"
        )
