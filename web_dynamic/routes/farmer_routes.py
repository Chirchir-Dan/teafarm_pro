#!/usr/bin/python3
"""
Module with functions to handle user registration,
login, and farmer_bp.dashboard access, as well as other farm management tasks.
"""
from flask import Blueprint, render_template, redirect,\
    url_for, flash, session, request, jsonify
from web_dynamic.forms.farmer_forms import (
    FarmerSignUpForm,
    FarmerSignInForm,
    AssignTaskForm,
    TrackTaskForm,
    # RecordDailySalesForm,
    RecordProductionForm,
    AddInventoryForm,
    EditInventoryForm,
    DeleteInventoryForm,
    LogExpenseForm,
    # AddEmployeeForm,
    # ManageEmployeeForm,
    # GenerateReportForm,
    UpdateProfileForm,
    ProductionFilterForm,
    LabourForm,)
from models.farmer import Farmer
from models.expense import Expense
from models.labour import Labour
from models.employee import Employee
from models.production import ProductionRecord
from models.market_value import MarketValue
from models.inventory import Inventory
from models import db
from datetime import datetime, timedelta
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash
from sqlalchemy import func
from math import ceil

farmer_bp = Blueprint('farmer_bp', __name__)


@farmer_bp.route('/', methods=['GET'])
def index():
    """Landing page"""
    return render_template('shared/index.html')


@farmer_bp.route('/dashboard')
@login_required
def dashboard():
    """Farmer dashboard with summary and recent activities"""

    current_month = datetime.now().strftime('%Y-%m')
    current_year = datetime.now().strftime('%Y')

    # Calculate total expenses
    total_expenses = db.session.query(db.func.sum(Expense.amount)).filter(
        db.func.date_format(Expense.date, '%Y,-%m') == current_month
    ).scalar() or 0

    # Calculate total tea produced
    total_tea_produced = db.session.query(
        db.func.sum(
            ProductionRecord.weight)).filter(
        db.func.date_format(
            ProductionRecord.date,
            '%Y-%m') == current_month).scalar() or 0

    # Total expenses for the current year
    total_expenses_year = db.session.query(db.func.sum(Expense.amount)).filter(
        db.func.date_format(Expense.date, '%Y') == current_year
    ).scalar() or 0

    # Total tea produced for the current year
    total_tea_produced_year = db.session.query(
        db.func.sum(
            ProductionRecord.weight)).filter(
        db.func.date_format(
            ProductionRecord.date,
            '%Y') == current_year).scalar() or 0

    # Calculate total inventory balance
    total_inventory_balance = db.session.query(
        db.func.sum(Inventory.quantity)).scalar() or 0

    return render_template(
        'farmer/farmer_dashboard.html',
        farmer=current_user,
        total_expenses=total_expenses,
        total_tea_produced=total_tea_produced,
        total_inventory_balance=total_inventory_balance,
        current_month=current_month,
        current_year=current_year,
        total_expenses_year=total_expenses_year,
        total_tea_produced_year=total_tea_produced_year
    )


@farmer_bp.route('/logout')
@login_required
def logout():
    """Logs out the current user."""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('public_bp.index'))


@farmer_bp.route('/assign_task', methods=['GET', 'POST'])
@login_required
def assign_task():
    """Assign and Track Tasks"""
    form = AssignTaskForm()
    # form.job_type.choices = [(labour.id, labour.type)
    # for labour in Labour.query.all()]
    # form.employee.choices = [(employee.id, employee.name)
    # for employee in Employee.query.all()]

    form.labour_types.choices = [(labour.id, labour.type)
                                 for labour in Labour.query.all()]
    form.employee.choices = [(employee.id, employee.name)
                             for employee in Employee.query.all()]

    if form.validate_on_submit():
        new_task = Task(
            labour_id=form.labour_types.data,
            employee_id=form.employee.data,
            due_date=form.due_date.data
        )
        db.session.add(new_task)
        db.session.commit()

        flash('Task assigned successfully!', 'success')
        return redirect(url_for('farmer_bp.dashboard'))
    return render_template('farmer/assign_task.html', form=form)


@farmer_bp.route('/record_production', methods=['GET', 'POST'])
@login_required
def record_production():
    form = RecordProductionForm()

    # Populate employee choices dynamically in the route
    employees = Employee.query.all()
    employee_choices = [(emp.id, emp.name) for emp in employees]
    for production_form in form.productions:
        production_form.employee_id.choices = employee_choices

    if request.method == 'GET':
        # Retrieve the most recent rate from MarketValue
        latest_rate_entry = MarketValue.query.order_by(
            MarketValue.date.desc()).first()
        latest_rate = latest_rate_entry.rate if latest_rate_entry else None
        # Set default rate if exists
        for production_form in form.productions:
            if latest_rate is not None:
                production_form.rate.data = latest_rate

    if form.validate_on_submit():
        # Loop through each production entry in the form
        for production_entry in form.productions.entries:
            employee_id = production_entry.employee_id.data
            weight = production_entry.weight.data
            rate = production_entry.rate.data or latest_rate
            date = form.plucking_date.data
            farmer_id=current_user.id

            # If no rate is provided, use the most recent rate
            if rate is None:
                latest_rate_entry = MarketValue.query.order_by(
                    MarketValue.date.desc()).first()
                rate = latest_rate_entry.rate if latest_rate_entry else 0

            # Validate rate
            if rate <= 0:
                flash('Rate must be provided and be greater\
                        than zero.', 'danger')
                return render_template(
                    'farmer/record_production.html',
                    form=form,
                    mode='record',
                    title='Record Production')

            # Fetch employee
            employee = Employee.query.get(employee_id)

            # Create new ProductionRecord with the rate
            production = ProductionRecord(
                employee_id=employee.id,
                date=date,
                weight=weight,
                rate=rate,
                farmer_id=farmer_id
            )

            db.session.add(production)
        db.session.commit()
        flash('Production recorded successfully!', 'success')
        return redirect(url_for('farmer_bp.record_production'))

    return render_template(
        'farmer/record_production.html',
        form=form,
        mode='record',
        title='Record Production')


@login_required
def get_weeks_of_year(year):
    weeks = []
    date = datetime(year, 1, 1)

    # Find the first Sunday of the year
    while date.weekday() != 6:
        date += timedelta(days=1)

    # Add week ranges (Sunday-Saturday)
    while date.year == year:
        end_of_week = date + timedelta(days=6)
        weeks.append(
            (f"{date.strftime('%Y-%m-%d')} to\
                    {end_of_week.strftime('%Y-%m-%d')}",
             f"{date.strftime('%b %d')} -\
                     {end_of_week.strftime('%b %d')}"))
        date += timedelta(days=7)

    return weeks

# In farmer_routes.py


@farmer_bp.route('/view_production', methods=['GET', 'POST'])
@login_required
def view_production():
    form = ProductionFilterForm()

    current_date = datetime.today()
    current_year = current_date.year
    current_month = current_date.month

    # Set choices dynamically
    form.year.choices = [(str(y), str(y)) for
                         y in range(current_year, current_year - 10, -1)]
    form.month.choices = [
        (str(m),
         datetime(
            current_year,
            m,
            1).strftime('%B')) for m in range(
            1,
            13)]
    weeks = get_weeks_of_year(current_year)
    form.week.choices = weeks

    # Set choices dynamically
    form.year.choices = [(str(y), str(y)) for
                         y in range(current_year, current_year - 10, -1)]
    form.month.choices = [(str(m),
                           datetime(current_year, m, 1).strftime('%B')) for
                          m in range(1, 13)]
    weeks = get_weeks_of_year(current_year)
    form.week.choices = weeks

    # Calculate current week for default week
    current_week_start = current_date - \
        timedelta(days=(current_date.weekday() + 1) % 7)
    current_week_end = current_week_start + timedelta(days=6)
    current_week_str = (
        f"{current_week_start.strftime('%Y-%m-%d')} "
        f"to {current_week_end.strftime('%Y-%m-%d')}"
    )
    default_week = next(
        (week[0] for week in weeks if week[0] == current_week_str),
        weeks[0][0])

    # Set defaults on GET request (initial load)
    if request.method == 'GET':
        form.year.process_data(str(current_year))
        form.month.process_data(str(current_month))

        form.week.process_data(default_week)

    total_weight = 0
    total_amount = 0
    production_records = []

    # Handle form submission
    if form.validate_on_submit():
        selected_date = form.date.data
        filter_by = form.filter_by.data
        selected_year = form.year.data
        selected_month = form.month.data
        selected_week = form.week.data

        # Prevent future date selection
        if selected_date > datetime.today().date():
            flash("Future dates are not allowed!", "danger")
        else:
            query = ProductionRecord.query

            if filter_by == 'day' and selected_date:
                production_records = query.filter_by(date=selected_date).all()

            elif filter_by == 'week' and selected_week:
                start_of_week, end_of_week =\
                    selected_week.split(" to ")
                start_of_week = datetime.strptime(start_of_week,
                                                  '%Y-%m-%d').date()
                end_of_week = datetime.strptime(end_of_week,
                                                '%Y-%m-%d').date()
                production_records = query.filter(
                    ProductionRecord.date >= start_of_week,
                    productionRecord.date <= end_of_week).all()

            elif filter_by == 'month' and selected_month and selected_year:
                production_records = query.filter(
                    db.extract('month', ProductionRecord. date) ==
                    int(selected_month),
                    db.extract('year', ProductionRecord.date) ==
                    int(selected_year)
                ).all()

            elif filter_by == 'year' and selected_year:
                production_records = query.filter(
                    db.extract('year', ProductionRecord.date) ==
                    int(selected_year)
                ).all()

            else:
                flash("Please select valid filtering\
                        criteria.", "danger")

            # Calculate total weight and amount paid
            total_weight = sum(record.weight for record in
                               production_records)
            total_amount = sum(record.amount_paid for
                               record in production_records)

    # Pass datetime to the template
    return render_template(
        'farmer/view_production.html',
        form=form,
        total_weight=total_weight,
        total_amount=total_amount,
        records=production_records,
        datetime=datetime,
        mode='view',
        title='View Production'
    )

@farmer_bp.route('/inventory', methods=['GET', 'POST'])
@login_required
def manage_inventory():
    page = request.args.get('page', 1, type=int)
    add_form = AddInventoryForm()
    edit_form = EditInventoryForm()
    delete_form = DeleteInventoryForm()

    farmer_id = current_user.id

    # Helper function to add an inventory item
    def add_inventory_item(item_name, quantity):
        try:
            existing_item = Inventory.query.filter_by(item_name=item_name, farmer_id=farmer_id).first()
            if existing_item:
                flash(f'Item "{item_name}" already exists. Please use the update option to modify its quantity.', 'warning')
            else:
                new_inventory = Inventory(item_name=item_name, quantity=quantity, farmer_id=farmer_id)
                db.session.add(new_inventory)
                db.session.commit()
                flash(f'Inventory item "{item_name}" added successfully!', 'success')
        except Exception as e:
            db.session.rollback()  # Rollback any changes if an error occurs
            flash(f"Error adding inventory: {str(e)}", 'danger')

    # Helper function to update inventory quantity
    def update_inventory_quantity(item_id, quantity):
        try:
            inventory = Inventory.query.get(item_id)
            if inventory and inventory.farmer_id == farmer_id:
                if inventory.quantity != quantity:
                    inventory.quantity = quantity
                    db.session.commit()
                    flash(f'Quantity of {inventory.item_name} updated successfully!', 'success')
                else:
                    flash(f'Quantity of {inventory.item_name} is already {inventory.quantity}. No update needed.', 'info')
            else:
                flash(f'Inventory item not found or permission denied.', 'danger')
        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            flash(f"Error updating inventory: {str(e)}", 'danger')

    # Helper function to delete an inventory item
    def delete_inventory_item(item_id):
        try:
            inventory = Inventory.query.get(item_id)
            if inventory and inventory.farmer_id == farmer_id:
                db.session.delete(inventory)
                db.session.commit()
                flash(f'Inventory item "{inventory.item_name}" deleted successfully.', 'success')
            else:
                flash(f'Inventory item not found or permission denied.', 'danger')
        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            flash(f"Error deleting inventory item: {str(e)}", 'danger')

    # Add Inventory
    if add_form.validate_on_submit():
        item_name = add_form.item_name.data
        quantity = add_form.quantity.data
        add_inventory_item(item_name, quantity)
        return redirect(url_for('farmer_bp.manage_inventory'))

    # Edit Inventory
    if edit_form.validate_on_submit() and request.form.get('edit_submit'):
        item_id = edit_form.item_id.data
        quantity = edit_form.quantity.data
        update_inventory_quantity(item_id, quantity)
        return redirect(url_for('farmer_bp.manage_inventory'))

    # Delete Inventory
    if delete_form.validate_on_submit():
        item_id = delete_form.item_id.data
        delete_inventory_item(item_id)
        return redirect(url_for('farmer_bp.manage_inventory'))

    # Pagination and Render
    inventories = Inventory.query.filter_by(farmer_id=farmer_id).paginate(page=page, per_page=10)
    return render_template('farmer/inventory.html',
                           add_form=add_form, edit_form=edit_form,
                           delete_form=delete_form, inventories=inventories)


@farmer_bp.route('/expenses', methods=['GET', 'POST'])
@login_required
def expenses():
    """Log Operational Expenses"""
    form = LogExpenseForm()
    form.category.choices = [(labour.id, labour.type) for
                             labour in Labour.query.all()]

    if not form.category.choices:
        flash('No labour categories available. Please add categories first.', 'warning')
        return redirect(url_for('farmer_bp.dashboard'))

    if form.validate_on_submit():
        labour_instance = Labour.query.get(form.category.data)
        
        if not labour_instance:
            flash('Invalid labour category selected.', 'error')
            return redirect(url_for('farmer_bp.expenses'))

        new_expense = Expense(
            category=labour_instance,
            description=form.description.data,
            amount=form.amount.data,
            date=form.date.data,
            farmer_id=current_user.id
        )
        try:
            db.session.add(new_expense)
            db.session.commit()
            flash('Expense logged successfully!', 'success')
            return redirect(url_for('farmer_bp.expenses'))

        except Exception as e:
            db.session.rollback()
            flash('An error occurred while logging the expense. Please try again.', 'error')

    return render_template('farmer/expenses.html', form=form)


@farmer_bp.route('/employees/list', methods=['GET'])
@login_required
def list_employees():
    """Lists all Employees with their job types"""
    employees = Employee.query.order_by(Employee.name).all()
    job_types = Labour.query.all()

    return render_template(
        'farmer/employee_list.html',
        employees=employees,
        job_types=job_types)


@farmer_bp.route('/add_employee/', methods=['POST'])
@login_required
def add_employee():
    """Add a new employee"""
    data = request.get_json()

    name = data.get('name')
    phone_number = data.get('phone_number')
    email = data.get('email')
    password = data.get('password')
    job_type_id = data.get('job_type')

    if not all([name, phone_number, password, job_type_id]):
        return jsonify({
            'status': 'error',
            'message': 'Please fill the required sections'}), 400

    if Employee.query.filter_by(phone_number=phone_number).first():
        return jsonify({
            'status': 'error',
            'message': 'An employee with this phone number already exists.'
        }), 400

    job_type = Labour.query.get(job_type_id)
    if not job_type:
        return jsonify({
            'status': 'error',
            'message': 'Invalid job type'
        }), 400

    try:
        # Hash the password
        password_hash = generate_password_hash(password)

        # Create new Employee object
        new_employee = Employee(
            name=name,
            phone_number=phone_number,
            email=email,
            password_hash=password_hash,
            job_type=job_type,
            farmer_id=current_user.id
        )

        db.session.add(new_employee)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Employee added successfully!'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to add employee. Please try again'
        }), 500




@farmer_bp.route('/update_employee/<employee_id>/',
                 methods=['PUT'])
@login_required
def update_employee(employee_id):
    """Update the employee details"""
    employee = Employee.query.get(employee_id)

    if not employee:
        return jsonify({'status': 'error', 'message':
                        'Employee not found!'}), 404

    data = request.get_json()
    employee.name = data.get('name')
    employee.phone_number = data.get('phone_number')
    job_type_id = data.get('job_type')
    labour_instance = Labour.query.get(job_type_id)

    if labour_instance:
        employee.job_type = labour_instance

    db.session.commit()
    return jsonify({'status': 'success', 'message':
                    'Employee updated successfully!'})


@farmer_bp.route('/delete_employee/<employee_id>/',
                 methods=['DELETE'])
@login_required
def delete_employee(employee_id):
    """Deletes an Employee"""
    employee = Employee.query.get(employee_id)

    if not employee:
        return jsonify({'status': 'error', 'message':
                        'Employee not found'}), 404

    db.session.delete(employee)
    db.session.commit()
    return jsonify({'status': 'success', 'message':
                    'Employee deleted successfully'})


@farmer_bp.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    """Route for updating farmer's profile"""
    form = UpdateProfileForm()

    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'error')
            return redirect(url_for('farmer_bp.update_profile'))

        current_user.name = form.name.data
        current_user.phone_number = form.phone_number.data
        current_user.email = form.email.data
        current_user.farm_name = form.farm_name.data
        current_user.location = form.location.data
        current_user.total_acreage = form.total_acreage.data

        if form.new_password.data:
            if form.new_password.data != form.confirm_password.data:
                flash('New passwords do not match.', 'error')
                return redirect(url_for('farmer_bp.update_profile'))
            current_user.set_password(form.new_password.data)

        # Save the changes
        current_user.save()

        flash('Profile updated successfully.', 'success')
        return redirect(url_for('farmer_bp.dashboard'))

    # Pre-fill form with current user data
    form.name.data = current_user.name
    form.phone_number.data = current_user.phone_number
    form.email.data = current_user.email
    form.farm_name.data = current_user.farm_name
    form.location.data = current_user.location
    form.total_acreage.data = current_user.total_acreage

    return render_template('farmer/update_profile.html', form=form)


@farmer_bp.route('/create_labour', methods=['GET', 'POST'])
@login_required
def create_labour():
    """Create new labour types and rates"""
    form = LabourForm()
    if form.validate_on_submit():
        labour_type = form.labour_type.data.strip()
        description = form.description.data.strip()
        rate = form.rate.data
        farmer_id = current_user.id
        
        existing_labour = Labour.query.filter_by(type=labour_type,
                farmer_id=farmer_id).first()
        if existing_labour:
            flash('Labour type already exists.', 'error')
            return redirect(url_for('farmer_bp.create_labour'))

        try:
            new_labour = Labour(
                type=labour_type,
                description=description,
                rate=rate,
                farmer_id=farmer_id
            )
            db.session.add(new_labour)
            db.session.commit()
            
            flash("Labour type '{labour_type}' created successfully!", "success")
            return redirect(url_for('farmer_bp.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occured while creating the labour type: {str(e)}",
                    "error")
            return redirect(url_for('farmer_bp.create_labour'))

    return render_template('farmer/create_labour.html', form=form)


@farmer_bp.route('/manage_labour', methods=['GET', 'POST'])
@login_required
def manage_labour():
    """Manage existing labour types"""
    form = LabourForm()
    labours = Labour.query.all()

    if form.validate_on_submit():
        labour_type = form.labour_type.data
        rate = form.rate.data

        # Check if labour type exists
        existing_labour = Labour.query.filter_by(type=labour_type).first()
        if existing_labour:
            # Update existing labour type
            existing_labour.rate = rate
            db.session.commit()
            flash('Labour type updated successfully!', 'success')
            return redirect(url_for('farmer_bp.manage_labour'))

        flash('Labour type not found.', 'error')

    return render_template(
        'farmer/manage_labour.html',
        form=form,
        labours=labours)
