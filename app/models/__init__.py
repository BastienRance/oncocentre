"""
Database models for the CARPEM Oncocentre application
"""

from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

# Import models
from .user import User
from .patient import Patient

__all__ = ['db', 'User', 'Patient']