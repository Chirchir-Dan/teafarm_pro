#!/usr/bin/python3
"""
Task Model represents the tasks assigned to employees.
"""

from models.base_model import BaseModel, db
from datetime import datetime


class Task(BaseModel):
    """Task Model represents the tasks assigned to employees."""
    __tablename__ = 'tasks'

    labour_id = db.Column(
        db.String(128),
        db.ForeignKey('labours.id'),
        nullable=False)
    employee_id = db.Column(
        db.String(128),
        db.ForeignKey('employees.id'),
        nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(128), default='Pending')

    # Relationships
    employee = db.relationship('Employee', back_populates='tasks')
    labour = db.relationship('Labour', back_populates='tasks')

    def __repr__(self):
        return f"< Task(id={self.id}, labour_type={self.labour.type}, "\
               f"employee={self.employee.name}, status={self.status}) >"
