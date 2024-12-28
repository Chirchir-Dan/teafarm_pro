#!/usr/bin/python3

"""
BaseModel module
Contains the BaseModel class from which future classes will be derived
"""

from datetime import datetime
import uuid
from . import db  # Import db from models/__init__.py


class BaseModel(db.Model):
    """The BaseModel class from which future classes will be derived"""
    __abstract__ = True  # Indicates that this class is an abstract base

    id = db.Column(db.String(60), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow)

    def __init__(self, *args, **kwargs):
        """Initialization of base model"""
        if kwargs:
            for key, value in kwargs.items():
                if key != "__class__":
                    setattr(self, key, value)
            if kwargs.get("created_at", None) and isinstance(
                    self.created_at, str):
                self.created_at = datetime.strptime(
                    kwargs["created_at"], "%Y-%m-%dT%H:%M:%S.%f")
            else:
                self.created_at = datetime.utcnow()
            if kwargs.get("updated_at", None) and isinstance(
                    self.updated_at, str):
                self.updated_at = datetime.strptime(
                    kwargs["updated_at"], "%Y-%m-%dT%H:%M:%S.%f")
            else:
                self.updated_at = datetime.utcnow()
            if kwargs.get("id", None) is None:
                self.id = str(uuid.uuid4())
        else:
            self.id = str(uuid.uuid4())
            self.created_at = datetime.utcnow()
            self.updated_at = self.created_at

    def save(self):
        """Updates the attribute 'updated_at' with the current
        datetime and saves the instance"""
        self.updated_at = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete the current instance from the storage"""
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        """Return a string representation of the instance"""
        return f"<{self.__class__.__name__} (id={self.id})>"
