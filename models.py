from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import bcrypt
from cryptography.fernet import Fernet
import os
import base64

db = SQLAlchemy()

def get_encryption_key():
    """Get or create encryption key for database fields"""
    key_path = 'encryption.key'
    if os.path.exists(key_path):
        with open(key_path, 'rb') as key_file:
            return key_file.read()
    else:
        key = Fernet.generate_key()
        with open(key_path, 'wb') as key_file:
            key_file.write(key)
        return key

ENCRYPTION_KEY = get_encryption_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

class User(UserMixin, db.Model):
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
    
    def __repr__(self):
        return f'<User {self.username}>'

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ipp_encrypted = db.Column(db.Text, nullable=False)  # Encrypted IPP
    first_name_encrypted = db.Column(db.Text, nullable=False)  # Encrypted first name
    last_name_encrypted = db.Column(db.Text, nullable=False)  # Encrypted last name
    birth_date_encrypted = db.Column(db.Text, nullable=False)  # Encrypted birth date
    sex = db.Column(db.String(1), nullable=False)  # M or F (not encrypted as less sensitive)
    oncocentre_id = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationship
    creator = db.relationship('User', backref=db.backref('patients', lazy=True))
    
    def _encrypt_data(self, data):
        """Encrypt sensitive data"""
        if isinstance(data, str):
            return cipher_suite.encrypt(data.encode()).decode()
        return cipher_suite.encrypt(str(data).encode()).decode()
    
    def _decrypt_data(self, encrypted_data):
        """Decrypt sensitive data"""
        return cipher_suite.decrypt(encrypted_data.encode()).decode()
    
    @property
    def ipp(self):
        """Decrypt and return IPP"""
        return self._decrypt_data(self.ipp_encrypted)
    
    @ipp.setter
    def ipp(self, value):
        """Encrypt and store IPP"""
        self.ipp_encrypted = self._encrypt_data(value)
    
    @property
    def first_name(self):
        """Decrypt and return first name"""
        return self._decrypt_data(self.first_name_encrypted)
    
    @first_name.setter
    def first_name(self, value):
        """Encrypt and store first name"""
        self.first_name_encrypted = self._encrypt_data(value)
    
    @property
    def last_name(self):
        """Decrypt and return last name"""
        return self._decrypt_data(self.last_name_encrypted)
    
    @last_name.setter
    def last_name(self, value):
        """Encrypt and store last name"""
        self.last_name_encrypted = self._encrypt_data(value)
    
    @property
    def birth_date(self):
        """Decrypt and return birth date"""
        from datetime import datetime
        date_str = self._decrypt_data(self.birth_date_encrypted)
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    
    @birth_date.setter
    def birth_date(self, value):
        """Encrypt and store birth date"""
        if hasattr(value, 'strftime'):
            date_str = value.strftime('%Y-%m-%d')
        else:
            date_str = str(value)
        self.birth_date_encrypted = self._encrypt_data(date_str)
    
    def __repr__(self):
        return f'<Patient {self.oncocentre_id}>'