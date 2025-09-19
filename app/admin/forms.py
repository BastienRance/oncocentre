"""
Administrative forms
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, ValidationError
import sqlite3

def check_username_exists(username):
    """Check if username exists using direct database access as fallback"""
    try:
        # Try SQLAlchemy first
        from ..core.models import User
        user = User.query.filter_by(username=username).first()
        return user is not None
    except Exception:
        # SQLAlchemy has cached metadata issues, use direct database access
        try:
            conn = sqlite3.connect('instance/oncocentre.db')
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM user WHERE username = ?", (username,))
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except Exception:
            return False

class CreateUserForm(FlaskForm):
    """User creation form for administrators"""
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    is_admin = BooleanField('Administrator privileges')
    is_principal_investigator = BooleanField('Principal investigator privileges')
    submit = SubmitField('Create User')
    
    def validate_username(self, username):
        if check_username_exists(username.data):
            raise ValidationError('Username already exists.')
    
    def validate_confirm_password(self, confirm_password):
        if self.password.data != confirm_password.data:
            raise ValidationError('Passwords must match.')

class EditUserForm(FlaskForm):
    """User editing form for administrators"""
    is_active = BooleanField('Account active')
    is_admin = BooleanField('Administrator privileges')
    is_principal_investigator = BooleanField('Principal investigator privileges')
    reset_password = PasswordField('New Password (leave blank to keep current)')
    confirm_password = PasswordField('Confirm New Password')
    submit = SubmitField('Update User')
    
    def validate_confirm_password(self, confirm_password):
        if self.reset_password.data and self.reset_password.data != confirm_password.data:
            raise ValidationError('Passwords must match.')