from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField, StringField, PasswordField, BooleanField, SelectField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, EqualTo, NumberRange, ValidationError, Email, Optional, Length
from app import db
from app.models import User
from app.static.dt_lists import days, time_slots
import datetime


class ChooseForm(FlaskForm):
    choice = HiddenField('Choice')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class AvailabilityForm(FlaskForm):
    days = days
    time_slots = time_slots
    for day_code, day_name in days:
        for time_code, time_name in time_slots:
            field_name = f'{day_code}_{time_code}'
            field_label = f'{day_name} {time_name}'
            locals()[field_name] = BooleanField(field_label)

    submit = SubmitField('Save Availability')