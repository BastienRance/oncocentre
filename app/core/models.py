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


class WhitelistEntry(db.Model):
    """Whitelist entry model for managing authorized users"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(255), nullable=True)  # Optional description/reason

    # Relationship to creator
    creator = db.relationship('User', backref='whitelist_entries')

    @classmethod
    def get_authorized_usernames(cls):
        """Get all active usernames from the whitelist"""
        entries = cls.query.filter_by(is_active=True).all()
        return set(entry.username for entry in entries)

    @classmethod
    def is_username_authorized(cls, username):
        """Check if a username is in the active whitelist"""
        entry = cls.query.filter_by(username=username, is_active=True).first()
        return entry is not None

    @classmethod
    def add_username(cls, username, created_by_id, description=None):
        """Add a username to the whitelist"""
        existing = cls.query.filter_by(username=username).first()
        if existing:
            # Reactivate if exists but inactive
            if not existing.is_active:
                existing.is_active = True
                existing.description = description or existing.description
                db.session.commit()
                return existing
            return None  # Already exists and active

        # Create new entry
        entry = cls(
            username=username,
            created_by=created_by_id,
            description=description,
            is_active=True
        )
        db.session.add(entry)
        db.session.commit()
        return entry

    @classmethod
    def remove_username(cls, username):
        """Remove a username from the whitelist (deactivate)"""
        entry = cls.query.filter_by(username=username, is_active=True).first()
        if entry:
            entry.is_active = False
            db.session.commit()
            return True
        return False

    @classmethod
    def migrate_from_env(cls, created_by_id):
        """Migrate existing AUTHORIZED_USERS environment variable to database"""
        from ..auth.views import get_authorized_users
        env_users = get_authorized_users()

        # Get existing usernames in DB
        existing_usernames = set(entry.username for entry in cls.query.all())

        # Add missing usernames from environment
        added_count = 0
        for username in env_users:
            if username not in existing_usernames:
                cls.add_username(username, created_by_id, "Migrated from environment variable")
                added_count += 1

        return added_count

    def __repr__(self):
        return f'<WhitelistEntry {self.username} ({"active" if self.is_active else "inactive"})>'