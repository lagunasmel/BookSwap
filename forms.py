from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class RegistrationForm(FlaskForm):
    """
Username is removed currently. -- Ben 11/5/20
username = StringField('Username',
                           # These are validators to make sure the input is valid
                           validators=[DataRequired(), Length(min=5, max=25)])
    """
    email = StringField('Username (Must be a valid email address)',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=5)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    fName = StringField('First Name', validators=[DataRequired()])
    lName = StringField('Last Name', validators=[DataRequired()])
    streetAddress = StringField('Street Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    postCode = StringField('Post Code', validators=[DataRequired()])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=5)])
    remember = BooleanField('Remember Me')  # will allow users to stay logged in
    submit = SubmitField('Login')
