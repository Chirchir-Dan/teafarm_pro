#!/usr/bin/python3
"""Module for employee-related forms"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from models.labour import Labour
from models import db


class EmployeeSignUpForm(FlaskForm):
    """Implements employee sign up form"""
    name = StringField('Name', validators=[DataRequired(), Length(max=128)])
    phone_number = StringField(
        'Phone Number', validators=[
            DataRequired(), Length(
                min=10, max=10)])
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            Length(
                max=128)])

    # Fetch job types from Labour model
    job_type = SelectField('Job Type', choices=[], validators=[DataRequired()])

    password = PasswordField(
        'Password', validators=[
            DataRequired(), Length(
                min=8)])
    confirm_password = PasswordField(
        'Confirm Password', validators=[
            DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def __init__(self, *args, **kwargs):
        """
        Initializes an EmployeeSignUpForm instance.
        """
        super().__init__(*args, **kwargs)
        # Populate job types using Labour's get_job_types method
        self.job_type.choices = Labour.get_job_types(db.session)


class EmployeeSignInForm(FlaskForm):
    """Implements employee sign in form"""
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            Length(
                max=128)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class UpdateProfileForm(FlaskForm):
    """Form to update employee profile"""
    name = StringField('Name', validators=[DataRequired(), Length(max=128)])
    phone_number = StringField(
        'Phone Number', validators=[
            DataRequired(), Length(
                min=10, max=10)])
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            Length(
                max=128)])
    password = PasswordField('New Password', validators=[Length(min=8)])
    confirm_password = PasswordField(
        'Confirm New Password', validators=[
            EqualTo('password')])
    submit = SubmitField('Update Profile')
