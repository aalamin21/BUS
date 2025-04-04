from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField, StringField, PasswordField, BooleanField, SelectField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, EqualTo, NumberRange, ValidationError, Email, Optional, Length
from app import db
from app.models import User
import datetime


class ChooseForm(FlaskForm):
    choice = HiddenField('Choice')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class AvailabilityForm(FlaskForm):
    time_slots = [
        ('0900', '09:00 AM'),
        ('1000', '10:00 AM'),
        ('1100', '11:00 AM'),
        ('1200', '12:00 PM'),
        ('1300', '1:00 PM'),
        ('1400', '2:00 PM'),
        ('1500', '3:00 PM'),
        ('1600', '4:00 PM'),
        ('1700', '5:00 PM'),
        ('1800', '6:00 PM')
    ]

    days = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday')
    ]

    for day_code, day_name in days:
        for time_code, time_name in time_slots:
            field_name = f'{day_code}_{time_code}'
            field_label = f'{day_name} {time_name}'
            locals()[field_name] = BooleanField(field_label)

    submit = SubmitField('Save Availability')