"""
User model for authentication and authorization
"""

from flask_login import UserMixin
from datetime import datetime
import bcrypt
from . import db

class User(UserMixin, db.Model):
    """User model for authentication and user management"""
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Hash and set password"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    @property
    def patient_count(self):
        """Get the number of patients created by this user"""
        from .patient import Patient
        return Patient.query.filter_by(created_by=self.id).count()
    
    def __repr__(self):
        return f'<User {self.username}>'