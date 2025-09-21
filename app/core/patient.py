"""
Patient model with encrypted sensitive data
"""

# Re-export Patient from models for backward compatibility
from .models import Patient

__all__ = ['Patient']