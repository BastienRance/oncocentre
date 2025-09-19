"""
Forms for the CARPEM Oncocentre application
"""

from .auth import LoginForm
from .patient import PatientForm
from .admin import CreateUserForm, EditUserForm

__all__ = [
    'LoginForm',
    'PatientForm', 
    'CreateUserForm',
    'EditUserForm'
]