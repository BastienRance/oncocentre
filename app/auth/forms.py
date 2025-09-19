"""
Authentication forms
"""

from flask import current_app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length, Optional

class LoginForm(FlaskForm):
    """User login form with dual authentication support"""
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    auth_method = RadioField(
        'Authentication Method',
        choices=[('auto', 'Auto-detect'), ('local', 'Local Account'), ('ldap', 'LDAP/Active Directory')],
        default='auto',
        validators=[Optional()]
    )
    submit = SubmitField('Sign In')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configure authentication method choices based on app configuration
        choices = []
        
        # Always include auto-detect if both methods are available
        if (getattr(current_app.config, 'ALLOW_LOCAL_AUTH', True) and 
            getattr(current_app.config, 'ALLOW_LDAP_AUTH', True)):
            choices.append(('auto', 'Auto-detect'))
        
        # Add local authentication if enabled
        if getattr(current_app.config, 'ALLOW_LOCAL_AUTH', True):
            choices.append(('local', 'Local Account'))
        
        # Add LDAP authentication if enabled
        if getattr(current_app.config, 'ALLOW_LDAP_AUTH', True):
            choices.append(('ldap', 'LDAP/Active Directory'))
        
        # Update choices
        if choices:
            self.auth_method.choices = choices
            if len(choices) == 1:
                # If only one method is available, hide the choice
                self.auth_method.default = choices[0][0]
        else:
            # Fallback to local if no configuration is available
            self.auth_method.choices = [('local', 'Local Account')]
            self.auth_method.default = 'local'