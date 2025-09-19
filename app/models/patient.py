"""
Patient model with encrypted sensitive data
"""

from datetime import datetime
from . import db
from ..utils.crypto import encrypt_data, decrypt_data

class Patient(db.Model):
    """Patient model with encrypted sensitive fields"""
    
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
    
    @property
    def ipp(self):
        """Decrypt and return IPP"""
        return decrypt_data(self.ipp_encrypted)
    
    @ipp.setter
    def ipp(self, value):
        """Encrypt and store IPP"""
        self.ipp_encrypted = encrypt_data(value)
    
    @property
    def first_name(self):
        """Decrypt and return first name"""
        return decrypt_data(self.first_name_encrypted)
    
    @first_name.setter
    def first_name(self, value):
        """Encrypt and store first name"""
        self.first_name_encrypted = encrypt_data(value)
    
    @property
    def last_name(self):
        """Decrypt and return last name"""
        return decrypt_data(self.last_name_encrypted)
    
    @last_name.setter
    def last_name(self, value):
        """Encrypt and store last name"""
        self.last_name_encrypted = encrypt_data(value)
    
    @property
    def birth_date(self):
        """Decrypt and return birth date"""
        date_str = decrypt_data(self.birth_date_encrypted)
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    
    @birth_date.setter
    def birth_date(self, value):
        """Encrypt and store birth date"""
        if hasattr(value, 'strftime'):
            date_str = value.strftime('%Y-%m-%d')
        else:
            date_str = str(value)
        self.birth_date_encrypted = encrypt_data(date_str)
    
    def __repr__(self):
        return f'<Patient {self.oncocentre_id}>'