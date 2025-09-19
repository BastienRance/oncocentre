"""
Administration module for CARPEM Oncocentre
Handles user management, admin dashboard, and system administration
"""

from .views import admin_bp
from .forms import CreateUserForm, EditUserForm

__all__ = ['admin_bp', 'CreateUserForm', 'EditUserForm']