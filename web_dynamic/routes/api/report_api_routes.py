#!/usr/bin/env python3
"""
Routes for generating reports for the farmer dynamically from models
"""
from flask import Blueprint, request, jsonify, abort, send_file, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.production import ProductionRecord
from models.expense import Expense
import datetime
from io import BytesIO
from weasyprint import HTML

# Blueprint setup
report_bp = Blueprint('report_bp', __name__)

# Allowed values for validation
ALLOWED_REPORT_TYPES = {'production', 'expenses'}
ALLOWED_TIME_FRAMES = {'daily', 'weekly', 'monthly'}

# Route: Generate a report based on report type and time frame
@report_bp.route('/reports', methods=['POST'])
@jwt_required()
def generate_report():
    """
    Generate a farm-related report based on report type and time frame.
    """
    current_farmer_id = get_jwt_identity()

    # Validate input data
    data = request.get_json()
    if not data:
        abort(400, description="Request body must be JSON.")

    report_type = data.get('report_type')
    time_frame = data.get('time_frame')

    # Check if the report_type is valid
    if report_type not in ALLOWED_REPORT_TYPES:
        # Return a 400 error with a message for invalid report_type
        return jsonify({
            'error': f"Invalid report type '{report_type}'. Supported types are: {ALLOWED_REPORT_TYPES}."
        }), 400

    # Check if the time_frame is valid
    if time_frame not in ALLOWED_TIME_FRAMES:
        # Return a 400 error with a message for invalid time_frame
        return jsonify({
            'error': f"Invalid time frame '{time_frame}'. Supported frames are: {ALLOWED_TIME_FRAMES}."
        }), 400

    # Generate report data dynamically
    report_data = generate_report_data(report_type, time_frame, current_farmer_id)
    if not report_data:
        abort(404, description="No data available for the requested report.")

    # Return the generated report data or PDF
    if 'pdf' in request.args:  # Check if the 'pdf' query parameter is present
        return generate_pdf_report(report_data, report_type, time_frame)

    return jsonify({
        "report_type": report_type,
        "time_frame": time_frame,
        "data": report_data
    }), 200

def generate_report_data(report_type, time_frame, farmer_id):
    """
    Generate report data based on report type and time frame.
    """
    if report_type == 'production':
        return generate_production_report(time_frame, farmer_id)
    elif report_type == 'expenses':
        return generate_expense_report(time_frame, farmer_id)
    return None

def generate_production_report(time_frame, farmer_id):
    """
    Generate a production report dynamically based on the time frame.
    """
    today = datetime.date.today()
    report_data = []

    if time_frame == 'daily':
        productions = ProductionRecord.query.filter_by(farmer_id=farmer_id, date=today).all()
    elif time_frame == 'weekly':
        start_date = today - datetime.timedelta(days=today.weekday())  # Start of the week (Monday)
        productions = ProductionRecord.query.filter(
            ProductionRecord.farmer_id == farmer_id,
            ProductionRecord.date.between(start_date, today)
        ).all()
    elif time_frame == 'monthly':
        start_date = today.replace(day=1)
        productions = ProductionRecord.query.filter(
            ProductionRecord.farmer_id == farmer_id,
            ProductionRecord.date.between(start_date, today)
        ).all()
    else:
        abort(400, description="Invalid time frame.")

    for production in productions:
        report_data.append({
            "date": production.date.isoformat(),
            "quantity": production.quantity,
            "employee": production.employee.name  # Ensure production.employee is an instance, not a string.
        })

    return report_data

def generate_expense_report(time_frame, farmer_id):
    """
    Generate an expense report dynamically based on the time frame.
    """
    today = datetime.date.today()
    report_data = []

    if time_frame == 'daily':
        expenses = Expense.query.filter_by(farmer_id=farmer_id, date=today).all()
    elif time_frame == 'weekly':
        start_date = today - datetime.timedelta(days=today.weekday())  # Start of the week (Monday)
        expenses = Expense.query.filter(
            Expense.farmer_id == farmer_id,
            Expense.date.between(start_date, today)
        ).all()
    elif time_frame == 'monthly':
        start_date = today.replace(day=1)
        expenses = Expense.query.filter(
            Expense.farmer_id == farmer_id,
            Expense.date.between(start_date, today)
        ).all()
    else:
        abort(400, description="Invalid time frame.")

    for expense in expenses:
        report_data.append({
            "date": expense.date.isoformat(),
            "amount": expense.amount,
            "category": expense.category
        })

    return report_data

def generate_pdf_report(report_data, report_type, time_frame):
    """
    Generate a PDF report using WeasyPrint and return it as a downloadable file.
    """
    # Render the HTML content for the report
    html_content = render_template(
        'report_template.html',
        report_type=report_type,
        time_frame=time_frame,
        report_data=report_data
    )

    # Convert HTML to PDF using WeasyPrint
    pdf = HTML(string=html_content).write_pdf()

    # Create a BytesIO buffer to return the PDF as a file
    buffer = BytesIO(pdf)
    buffer.seek(0)

    # Send the PDF as a downloadable file
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{report_type}_{time_frame}_report.pdf",
        mimetype='application/pdf'
    )
