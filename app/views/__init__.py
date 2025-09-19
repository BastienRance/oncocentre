"""
Views (route handlers) for the CARPEM Oncocentre application
"""

from .main import main_bp
from .auth import auth_bp
from .admin import admin_bp

__all__ = ['main_bp', 'auth_bp', 'admin_bp']