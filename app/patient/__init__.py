"""
Patient management module for CARPEM Oncocentre
Handles patient creation, listing, and identifier generation
"""

from .views import main_bp
from .forms import PatientForm

__all__ = ['main_bp', 'PatientForm']