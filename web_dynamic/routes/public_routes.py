#!/usr/bin/python3
"""
Module with functions to handle public-facing routes.
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user
from ..forms.farmer_forms import FarmerSignInForm
from ..forms.farmer_forms import FarmerSignUpForm
from ..forms.employee_forms import EmployeeSignInForm
from ..forms.employee_forms import EmployeeSignUpForm
from models.employee import Employee
from models.farmer import Farmer
from flask_login import login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db

public_bp = Blueprint(
    'public_bp',
    __name__,
    template_folder='templates/shared')


@public_bp.route('/')
def index():
    """Landing page"""
    return render_template('shared/index.html')


@public_bp.route('/signin', methods=['GET', 'POST'])
def signin():
    form_type = request.args.get('type', 'farmer')

    if form_type == 'employee':
        form = EmployeeSignInForm()
        if form.validate_on_submit():
            user = Employee.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                return redirect(url_for('public_bp.index'))
        return render_template('employee/employee_signin.html', form=form)

    form = FarmerSignInForm()
    if form.validate_on_submit():
        user = Farmer.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('public_bp.index'))
    return render_template('farmer/farmer_signin.html', form=form)


@public_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = FarmerSignUpForm()
    if form.validate_on_submit():

        existing_phone = Farmer.query.filter_by(
            phone_number=form.phone_number.data).first()
        if existing_phone:
            flash('A farmer with this phone number already exists. '
                  'Please choose a different phone number.', 'danger')
            return redirect(url_for('public_bp.signup'))

        new_farmer = Farmer(
            name=form.name.data,
            email=form.email.data,
            phone_number=form.phone_number.data,
            password_hash=generate_password_hash(form.password.data),
            farm_name=form.farm_name.data,
            location=form.location.data,
            total_acreage=form.total_acreage.data
        )
        try:
            db.session.add(new_farmer)
            db.session.commit()
            flash('Account Created Successfully!', 'Success')
            return redirect(url_for('public_bp.index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {e}", 'danger')
    return render_template('farmer/farmer_signup.html', form=form)


@public_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('public_bp.index'))


@public_bp.route('/privacy-policy')
def privacy_policy():
    return render_template('shared/privacy_policy.html')


@public_bp.route('/terms-of-service')
def terms_of_service():
    return render_template('shared/terms_of_service.html')
