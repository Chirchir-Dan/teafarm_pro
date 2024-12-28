from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField,\
    FloatField, SubmitField, FieldList, DateField,\
    FormField, DecimalField, TextAreaField, IntegerField,\
    HiddenField
from wtforms.validators import DataRequired, Email, Length,\
    EqualTo, NumberRange, Optional

from models.employee import Employee
from models import db
from models.labour import Labour
from datetime import datetime


class FarmerSignUpForm(FlaskForm):
    """Implements farmer sign up form"""
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
    farm_name = StringField(
        'Farm Name', validators=[
            Optional(), Length(
                max=128)])
    location = StringField(
        'Location', validators=[
            Optional(), Length(
                max=128)])
    total_acreage = FloatField('Total Acreage', validators=[DataRequired()])
    password = PasswordField(
        'Password', validators=[
            DataRequired(), Length(
                min=8)])
    confirm_password = PasswordField(
        'Confirm Password', validators=[
            DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class FarmerSignInForm(FlaskForm):
    """Implements farmer sign in form"""
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            Length(
                max=128)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class LabourForm(FlaskForm):
    labour_type = StringField('Labour Type', validators=[DataRequired()])
    rate = DecimalField('Rate', places=2, validators=[DataRequired()])
    submit = SubmitField('Submit')


class AssignTaskForm(FlaskForm):
    """Implements task assignment form"""
    labour_types = SelectField(
        'Labour Type',
        choices=[],
        validators=[
            DataRequired()])
    employee = SelectField(
        'Assign To',
        choices=[],
        validators=[
            DataRequired()])
    due_date = DateField(
        'Due Date',
        format='%Y-%m-%d',
        validators=[
            Optional()])
    submit = SubmitField('Assign Task')


class TrackTaskForm(FlaskForm):
    """Implements task tracking form"""
    task_id = SelectField('Task', coerce=int, validators=[DataRequired()])
    status = SelectField('Status',
                         choices=[('completed', 'Completed'),
                                  ('in_progress', 'In Progress')],
                         validators=[DataRequired()])
    submit = SubmitField('Update Status')


class ProductionForm(FlaskForm):
    """Form to record production details for an employee."""
    employee_id = SelectField('Employee', validators=[DataRequired()])
    weight = FloatField(
        'Weight (kg)',
        validators=[
            DataRequired(),
            NumberRange(
                min=0.1)])
    rate = FloatField(
        'Rate per kg',
        validators=[
            DataRequired(),
            NumberRange(
                min=0.01)])


class RecordProductionForm(FlaskForm):
    plucking_date = DateField(
        'Date',
        format='%Y-%m-%d',
        default=datetime.today,
        render_kw={"max": datetime.today().strftime('%Y-%m-%d')},
        validators=[DataRequired()]
    )
    productions = FieldList(FormField(ProductionForm), min_entries=1)
    submit = SubmitField('Record Production')


class ProductionFilterForm(FlaskForm):
    """
    Form to filter production records by day, week, month, or year.
    """
    filter_by = SelectField(
        'Filter by',
        choices=[('day', 'Day'), ('week', 'Week'),
                 ('month', 'Month'), ('year', 'Year')],
        validators=[DataRequired()]
    )
    date = DateField(
        'Select Date',
        format='%Y-%m-%d',
        validators=[DataRequired()],
        default=datetime.today
    )
    month = SelectField('Select Month', choices=[
        ('01', 'January'),
        ('02', 'February'),
        ('03', 'March'),
        ('04', 'April'),
        ('05', 'May'),
        ('06', 'June'),
        ('07', 'July'),
        ('08', 'August'),
        ('09', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December')
    ], default='01')

    week = SelectField('Select Week', choices=[], coerce=str)

    year = SelectField(
        'Select Year',
        choices=[],
        default=str(
            datetime.today().year))

    submit = SubmitField('Show Records')


class AddInventoryForm(FlaskForm):
    """Implements inventory management form"""
    item_name = StringField(
        'Item Name', validators=[
            DataRequired(), Length(
                max=128)])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Save Item')


class EditInventoryForm(FlaskForm):
    """Implements inventory usage tracking form"""
    item_id = HiddenField('Item ID')
    quantity = IntegerField('Quantity', validators=[DataRequired()])


class DeleteInventoryForm(FlaskForm):
    item_id = HiddenField('Item ID')
    delete_submit = SubmitField('Delete')


class LogExpenseForm(FlaskForm):
    """Form for logging an expense."""
    category = SelectField('Category', choices=[], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Length(max=255)])
    amount = FloatField(
        'Amount',
        validators=[
            DataRequired(),
            NumberRange(
                min=0.01,
                message="Amount must be positive")])
    date = DateField(
        'Date',
        format='%Y-%m-%d',
        default=datetime.today,
        render_kw={"max": datetime.today().strftime('%Y-%m-%d')}
    )
    submit = SubmitField('Log Expense')


"""class AddEmployeeForm(FlaskForm):
    Form for creating a new employee
    name = StringField('Name', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    email = StringField('Email', validators=[Optional()])
    job_type = SelectField('Job Type', choices=[], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Create Employee')

class ManageEmployeeForm(FlaskForm):
    Form for managing an employee
    employee = SelectField('Employee', choices=[], validators=[DataRequired()])
    job_type = SelectField('New Job Type', choices=[],
            validators=[DataRequired()])
    submit_update = SubmitField('Update Employee')
    submit_remove = SubmitField('Remove Employee')
"""


class GenerateReportForm(FlaskForm):
    """Form for generating a report"""
    report_type = SelectField('Report Type', choices=[
        ('daily', 'Daily Report'),
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('quarterly', 'Quarterly Report'),
        ('annual', 'Annual Report')],
        validators=[DataRequired()])
    start_date = DateField(
        'Start Date',
        format='%Y-%m-%d',
        validators=[
            DataRequired()])
    submit = SubmitField('Generate Report')


class UpdateProfileForm(FlaskForm):
    """Form for updating farmer's profile"""
    name = StringField('Name', validators=[DataRequired(), Length(max=128)])
    phone_number = StringField(
        'Phone Number', validators=[
            DataRequired(), Length(
                max=10)])
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            Length(
                max=128)])
    farm_name = StringField(
        'Farm Name', validators=[
            Optional(), Length(
                max=128)])
    location = StringField(
        'Location', validators=[
            Optional(), Length(
                max=128)])
    total_acreage = FloatField('Total Acreage', validators=[Optional()])
    current_password = PasswordField(
        'Current Password', validators=[
            DataRequired()])
    new_password = PasswordField(
        'New Password', validators=[
            Optional(), Length(
                min=8)])
    confirm_password = PasswordField(
        'Confirm New Password', validators=[
            Optional(), Length(
                min=8)])
    submit = SubmitField('Update Profile')
