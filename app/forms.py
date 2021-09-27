# This file is used to unify web forms and pass parameters to routes.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User

# Pass login parameters to routes.py
class LoginForm(FlaskForm):
    #actual need email, temp using username based on front end
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

# Pass registration parameters to routes.py
class RegistrationForm(FlaskForm):
    id = StringField('id', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

# Pass profile parameters to routes.py when user needs to update his/her personal info
class EditProfileForm(FlaskForm):
    id = StringField('id')
    phone = StringField('Phone')
    address = StringField('Address')
    description = TextAreaField('Description', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

