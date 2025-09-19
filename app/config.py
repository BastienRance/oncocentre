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