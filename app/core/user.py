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
    password_hash = db.Column(db.String(128), nullable=True)  # Nullable for LDAP users
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_principal_investigator = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # LDAP-specific fields
    auth_source = db.Column(db.String(20), default='local', nullable=False)  # 'local' or 'ldap'
    email = db.Column(db.String(120), nullable=True)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    display_name = db.Column(db.String(100), nullable=True)
    ldap_dn = db.Column(db.Text, nullable=True)  # LDAP Distinguished Name
    last_ldap_sync = db.Column(db.DateTime, nullable=True)  # Last sync with LDAP
    
    def set_password(self, password):
        """Hash and set password"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        if self.auth_source == 'ldap':
            # LDAP users don't have local passwords
            return False
        if not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    @property
    def patient_count(self):
        """Get the number of patients created by this user"""
        from .patient import Patient
        return Patient.query.filter_by(created_by=self.id).count()
    
    @classmethod
    def create_from_ldap(cls, ldap_info):
        """Create a new user from LDAP information"""
        user = cls(
            username=ldap_info.get('username'),
            auth_source='ldap',
            email=ldap_info.get('email', ''),
            first_name=ldap_info.get('first_name', ''),
            last_name=ldap_info.get('last_name', ''),
            display_name=ldap_info.get('display_name', ldap_info.get('username')),
            ldap_dn=ldap_info.get('dn', ''),
            last_ldap_sync=datetime.utcnow(),
            is_active=True
        )
        return user
    
    def update_from_ldap(self, ldap_info):
        """Update user information from LDAP"""
        self.email = ldap_info.get('email', self.email)
        self.first_name = ldap_info.get('first_name', self.first_name)
        self.last_name = ldap_info.get('last_name', self.last_name)
        self.display_name = ldap_info.get('display_name', self.display_name)
        self.ldap_dn = ldap_info.get('dn', self.ldap_dn)
        self.last_ldap_sync = datetime.utcnow()
    
    @property
    def full_name(self):
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.display_name:
            return self.display_name
        else:
            return self.username
    
    @property
    def is_ldap_user(self):
        """Check if user authenticates via LDAP"""
        return self.auth_source == 'ldap'
    
    def __repr__(self):
        return f'<User {self.username} ({self.auth_source})>'