from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField, StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email
from .availability_utils import days, time_slots
from .module_utils import module_list



class ChooseForm(FlaskForm):
    choice = HiddenField('Choice')

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    faculty = SelectField('Faculty', choices = [("Life Sciences", "Life Sciences")], validators=[DataRequired()])
    course_name = SelectField('Course Name', choices = [("Medicine and Surgery MBChB", "Medicine and Surgery MBChB")], validators=[DataRequired()])
    year_of_study = SelectField('Course Year', choices = [("First Year", "First Year")], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
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
            locals()[field_name] = BooleanField('')

    submit = SubmitField('Save Availability')

class ModuleForm(FlaskForm):
    module1 = SelectField('Module 1', choices=[(i, module) for i, module in module_list.items()],
                          validators=[DataRequired(message="Must select at least one module")])
    module2 = SelectField('Module 2', choices=[(i, module) for i, module in module_list.items()])
    module3 = SelectField('Module 3', choices=[(i, module) for i, module in module_list.items()])

    submit = SubmitField('Save Module Selections')

class VoteForm(FlaskForm):
    submit = SubmitField('Vote')

    @staticmethod
    def validate_module2(self, field):
        if int(field.data) != 0 and field.data == self.module1.data:
            raise ValidationError('Cannot select the same module twice')

    @staticmethod
    def validate_module3(self, field):
        if int(field.data) != 0 and (field.data == self.module2.data or field.data == self.module1.data):
            raise ValidationError('Cannot select the same module twice')