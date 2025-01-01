#!/usr/bin/python3
"""
Module with functions to handle employee-specific routes.
"""
from flask import (Blueprint, render_template, redirect,
                   url_for, flash, session)
from web_dynamic.forms.employee_forms import (
    EmployeeSignUpForm,
    EmployeeSignInForm
)
from models.employee import Employee

employee_bp = Blueprint('employee_bp', __name__)


@employee_bp.route('/', methods=['GET'])
def index():
    """Landing page for employees"""
    return render_template('shared/index.html')


@employee_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handles employee sign up"""
    form = EmployeeSignUpForm()
    if form.validate_on_submit():
        # Check if email or phone number already exists
        if (storage.get_by_email(Employee, form.email.data) or
                storage.get_by_phone(Employee, form.phone_number.data)):
            flash('Email or Phone Number already registered.', 'danger')
            return redirect(url_for('employee_bp.signup'))

        # Create a new Employee instance
        new_employee = Employee(
            name=form.name.data,
            phone_number=form.phone_number.data,
            email=form.email.data,
            job_type=form.job_type.data
        )
        new_employee.set_password(form.password.data)
        storage.new(new_employee)
        storage.save()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('employee_bp.signin'))
    return render_template('employee_signup.html', form=form)


@employee_bp.route('/signin', methods=['GET', 'POST'])
def employee_signin():
    """Handles signing in"""
    form = EmployeeSignInForm()
    if form.validate_on_submit():
        employee = storage.get_by_email(Employee, form.email.data)
        if employee and employee.check_password(form.password.data):
            session['employee_id'] = employee.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('employee_bp.dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('employee_signin.html', form=form)


@employee_bp.route('/dashboard')
def employee_dashboard():
    """Handles dashboard after logging in."""
    if 'employee_id' not in session:
        flash('Please log in to access the dashboard', 'danger')
        return redirect(url_for('public_bp.signin'))

    employee = storage.get(Employee, session['employee_id'])
    return render_template('employee_dashboard.html', employee=employee)


@employee_bp.route('/logout')
def employee_logout():
    """Handle logging out"""
    session.pop('employee_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('employee_bp.signin'))
