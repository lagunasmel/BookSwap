from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class RegistrationForm(FlaskForm):
    username = StringField('Username (will be displayed publicly)',
            validators=[DataRequired()])
    email = StringField('Email (for contacting purposes)',
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
    username = StringField('Username or Email',
                        validators=[DataRequired()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=5)])
    remember = BooleanField('Remember Me')  # will allow users to stay logged in
    submit = SubmitField('Login')

class BookSearchForm(FlaskForm):
    ISBN = StringField('ISBN')
    author = StringField("Author")
    title = StringField("Title")
    submit = SubmitField("Search For This Book")

class AccountSettingsChangeForm(FlaskForm):
    username = StringField('Username (will be displayed publicly)',
            validators=[DataRequired()])
    email = StringField('Email (for contacting purposes)',
                        validators=[DataRequired(), Email()])
    fName = StringField('First Name', validators=[DataRequired()])
    lName = StringField('Last Name', validators=[DataRequired()])
    streetAddress = StringField('Street Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    postCode = StringField('Post Code', validators=[DataRequired()])
    submit_account_change = SubmitField('Save Changes')

class PasswordChangeForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password (at least 5 characters)',
                             validators=[DataRequired(), Length(min=5)])
    confirm_new_password = PasswordField('Confirm New Password',
                             validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Save Changes')
 
