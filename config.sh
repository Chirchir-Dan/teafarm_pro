#!/usr/bin/bash

# Exit script on error
set -e

# Create and activate a virtual environment
echo "Setting up virtual environment..."
python3 -m venv venv

# Activate the virtual environment
# On Linux/macOS
source venv/bin/activate

# On Windows, uncomment the following line:
# .\venv\Scripts\activate

echo "Virtual environment activated."

# Install required packages inside the virtual environment
echo "Installing required Python packages from requirements.txt..."
pip install -r requirements.txt

# Install required packages inside the virtual environment
# echo "Installing required Python packages..."
# pip install --upgrade pip
# pip install flask flask_login flask_wtf mysqlclient flask_sqlalchemy Flask-Migrate email_validator

# Install system-level dependencies (not in virtual environment)
echo "Installing system-level dependencies..."
sudo apt-get update
sudo apt-get install -y pkg-config libmysqlclient-dev python3-pip gunicorn nginx certbot python3-certbot-nginx

echo "All required packages installed."

# Nginx and SSL setup (add if needed for production)
# Set up reverse proxy, configure SSL, etc.
# e.g., sudo systemctl restart nginx or set up SSL with Certbot

echo "Setup completed successfully!"
