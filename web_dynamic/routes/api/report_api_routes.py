#!/usr/bin/env python3
"""
Routes for generating reports for the farmer
"""
from flask import Blueprint, request, jsonify, abort, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
import datetime
from io import BytesIO
import os
from weasyprint import HTML

# Blueprint setup
report_bp = Blueprint('report', __name__, url_prefix='/api/reports')

# Route 1: Generate a report based on report type and time frame
@report_bp.route('', methods=['POST'])
@jwt_required()
def generate_report():
    """
    Generate a farm-related report based on report type and time frame.
    """
    current_farmer_id = get_jwt_identity()

    # Validate input data
    data = request.get_json()
    if 'report_type' not in data or 'time_frame' not in data:
        abort(400, description="Missing required fields (report_type, time_frame).")

    report_type = data['report_type']
    time_frame = data['time_frame']

    # Generate report data based on report type and time frame
    report_data = generate_report_data(report_type, time_frame)

    if not report_data:
        abort(400, description="Invalid report type or time frame.")

    # Return the generated report data or PDF
    if 'pdf' in request.args:  # Check if the 'pdf' query parameter is present
        return generate_pdf_report(report_data, report_type, time_frame)

    return jsonify({
        "report_type": report_type,
        "time_frame": time_frame,
        "data": report_data
    }), 200

def generate_report_data(report_type, time_frame):
    """
    Generate report data based on report type and time frame.
    """
    if report_type == 'production':
        return generate_production_report(time_frame)
    elif report_type == 'expenses':
        return generate_expense_report(time_frame)
    # Add other report types here as needed
    return None

def generate_production_report(time_frame):
    """
    Generate a production report based on the time frame (daily, monthly, etc.).
    """
    today = datetime.date.today()
    report_data = []

    if time_frame == 'daily':
        report_data.append({
            "date": today,
            "production": 120  # Example value
        })
    elif time_frame == 'monthly':
        for i in range(30):  # Simulate 30 days of production
            report_data.append({
                "date": today - datetime.timedelta(days=i),
                "production": 100 + i  # Example production values
            })

    return report_data

def generate_expense_report(time_frame):
    """
    Generate an expense report based on the time frame (daily, monthly, etc.).
    """
    today = datetime.date.today()
    report_data = []

    if time_frame == 'daily':
        report_data.append({
            "date": today,
            "expense": 50  # Example value
        })
    elif time_frame == 'monthly':
        for i in range(30):  # Simulate 30 days of expenses
            report_data.append({
                "date": today - datetime.timedelta(days=i),
                "expense": 150 + i  # Example expense values
            })

    return report_data

def generate_pdf_report(report_data, report_type, time_frame):
    """
    Generate a PDF report using WeasyPrint and return it as a downloadable file.
    """
    # Convert the report data to HTML format
    html_content = f"""
    <html>
    <head><title>{report_type.capitalize()} Report ({time_frame})</title></head>
    <body>
    <h1>{report_type.capitalize()} Report ({time_frame})</h1>
    <table border="1">
    <tr><th>Date</th><th>Amount</th></tr>
    """

    for entry in report_data:
        html_content += f"""
        <tr>
            <td>{entry['date']}</td>
            <td>{entry['expense'] if 'expense' in entry else entry['production']}</td>
        </tr>
        """

    html_content += "</table></body></html>"

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
