"""
Configuration settings for the CARPEM Oncocentre application
"""

import os

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'carpem-oncocentre-dev-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///oncocentre.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    
    # LDAP Configuration
    LDAP_ENABLED = os.environ.get('LDAP_ENABLED', 'false').lower() == 'true'
    LDAP_SERVER = os.environ.get('LDAP_SERVER', 'ldap://your-domain-controller.example.com')
    LDAP_PORT = int(os.environ.get('LDAP_PORT', '389'))
    LDAP_USE_SSL = os.environ.get('LDAP_USE_SSL', 'false').lower() == 'true'
    LDAP_DOMAIN = os.environ.get('LDAP_DOMAIN', 'YOURDOMAIN')
    LDAP_BASE_DN = os.environ.get('LDAP_BASE_DN', 'DC=yourdomain,DC=com')
    LDAP_USER_SEARCH_BASE = os.environ.get('LDAP_USER_SEARCH_BASE', 'OU=Users,DC=yourdomain,DC=com')
    LDAP_USER_SEARCH_FILTER = os.environ.get('LDAP_USER_SEARCH_FILTER', '(sAMAccountName={username})')
    LDAP_BIND_USER = os.environ.get('LDAP_BIND_USER', None)
    LDAP_BIND_PASSWORD = os.environ.get('LDAP_BIND_PASSWORD', None)
    LDAP_TIMEOUT = int(os.environ.get('LDAP_TIMEOUT', '10'))
    
    # Authentication settings
    ALLOW_LOCAL_AUTH = os.environ.get('ALLOW_LOCAL_AUTH', 'true').lower() == 'true'
    ALLOW_LDAP_AUTH = os.environ.get('ALLOW_LDAP_AUTH', 'true').lower() == 'true'
    AUTO_CREATE_LDAP_USERS = os.environ.get('AUTO_CREATE_LDAP_USERS', 'true').lower() == 'true'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///oncocentre.db'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}