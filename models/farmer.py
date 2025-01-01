"""
Defines the Farmer model
"""
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models.base_model import BaseModel, db

class Farmer(BaseModel, UserMixin):
    """
    Farmer model for representing a farm owner
    """
    __tablename__ = 'farmers'

    name = db.Column(db.String(128), nullable=False)
    phone_number = db.Column(db.String(10), nullable=False, unique=True)
    email = db.Column(db.String(128), nullable=False, unique=True)
    farm_name = db.Column(db.String(128), nullable=True)
    location = db.Column(db.String(128), nullable=True)
    total_acreage = db.Column(db.Float, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)

    employees = db.relationship('Employee', back_populates='farmer')

    def __init__(self, *args, **kwargs):
        """
        Initializes a new Farmer instance.
        """
        super().__init__(*args, **kwargs)

    def set_password(self, password):
        """Hashes the password and stores it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks the password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_farmer(self):
        return True

    @property
    def is_employee(self):
        return False

    def __repr__(self):
        """Return a string representation of the instance."""
        return (f"<Farmer(name={self.name}, email={self.email}, "
                f"farm_name={self.farm_name}, location={self.location}, "
                f"total_acreage={self.total_acreage})>")
