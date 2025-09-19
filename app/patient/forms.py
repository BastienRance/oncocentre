"""
Patient management forms
"""

from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class PatientForm(FlaskForm):
    """Patient creation form"""
    ipp = StringField('IPP', validators=[DataRequired(), Length(max=50)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=100)])
    birth_date = DateField('Birth Date', validators=[DataRequired()])
    sex = SelectField('Sex', choices=[('M', 'Male'), ('F', 'Female')], validators=[DataRequired()])
    submit = SubmitField('Create Patient')