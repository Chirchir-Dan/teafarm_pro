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
from models.task import Task
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

    job_type_id = db.Column(db.String(128), db.ForeignKey('labours.id'), nullable=False)
    farmer_id = db.Column(db.String(128), db.ForeignKey('farmers.id'), nullable=False)

    productions = db.relationship(
        'ProductionRecord',
        back_populates='employee')
    job_type = db.relationship('Labour', back_populates='employees')

    tasks = relationship('Task', back_populates='employee', overlaps="tasks, employees")
    farmer = relationship('Farmer', back_populates='employees')

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

    @property
    def is_farmer(self):
        return False

    @property
    def is_employee(self):
        return True

    def __repr__(self):
        """Return a string representation of the instance."""
        return f"< Employee(name={self.name}, "\
               f"id={self.id}, job_type={self.job_type}) >"
