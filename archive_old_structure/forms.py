from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, ValidationError
from models import User
import sqlite3

def check_username_exists(username):
    """Check if username exists using direct database access as fallback"""
    try:
        # Try SQLAlchemy first
        user = User.query.filter_by(username=username).first()
        return user is not None
    except Exception:
        # SQLAlchemy has cached metadata issues, use direct database access
        try:
            conn = sqlite3.connect('oncocentre.db')
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM user WHERE username = ?", (username,))
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except Exception:
            return False

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class PatientForm(FlaskForm):
    ipp = StringField('IPP', validators=[DataRequired(), Length(max=50)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=100)])
    birth_date = DateField('Birth Date', validators=[DataRequired()])
    sex = SelectField('Sex', choices=[('M', 'Male'), ('F', 'Female')], validators=[DataRequired()])
    submit = SubmitField('Create Patient')

class CreateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    is_admin = BooleanField('Administrator privileges')
    submit = SubmitField('Create User')
    
    def validate_username(self, username):
        if check_username_exists(username.data):
            raise ValidationError('Username already exists.')
    
    def validate_confirm_password(self, confirm_password):
        if self.password.data != confirm_password.data:
            raise ValidationError('Passwords must match.')

class EditUserForm(FlaskForm):
    is_active = BooleanField('Account active')
    is_admin = BooleanField('Administrator privileges')
    reset_password = PasswordField('New Password (leave blank to keep current)')
    confirm_password = PasswordField('Confirm New Password')
    submit = SubmitField('Update User')
    
    def validate_confirm_password(self, confirm_password):
        if self.reset_password.data and self.reset_password.data != confirm_password.data:
            raise ValidationError('Passwords must match.')