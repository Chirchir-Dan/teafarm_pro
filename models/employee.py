#!/usr/bin/python3
"""
Defines the Employee model
"""

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from models.base_model import BaseModel, db
from sqlalchemy.orm import relationship
from models.labour import Labour
from models.production import ProductionRecord

class Employee(BaseModel, UserMixin):
    """
    Represents an employee in the farm
    """
    __tablename__ = 'employees'

    name = db.Column(db.String(128), nullable=False)
    phone_number = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(128), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    labour_id = db.Column(db.String(128), db.ForeignKey('labours.id'), nullable=False)
    farmer_id = db.Column(db.String(128), db.ForeignKey('farmers.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('name', 'phone_number', 'farmer_id', name='unique_employee_name_phone_per_farmer'), )

    productions = db.relationship('ProductionRecord', back_populates='employee')
    job_type = db.relationship('Labour', back_populates='employees')
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
    
    def to_dict(self):
        """Return a dictionary representation of the instance."""
        employee_dict = {
            'id': self.id,
            'name': self.name,
            'phone_number': self.phone_number,
            'email': self.email,
            'labour_id': self.labour_id,
        }
        return employee_dict

    def __repr__(self):
        """Return a string representation of the instance."""
        return f"<Employee(name={self.name}, id={self.id}, job_type={self.job_type})>"
