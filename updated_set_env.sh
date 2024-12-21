#!/usr/bin/bash

# Exit script on error
set -e

# Prompt user to enter MySQL root password
read -sp "Enter your MySQL root password: " MYSQL_ROOT_PWD
echo # Move to a new line after password input

# Set PYTHONPATH to the current working directory
export FLASK_APP="$PWD/web_dynamic/app.py"
export PYTHONPATH="$PWD"

export TEAFARM_MYSQL_USER="teafarm_dev"
export TEAFARM_MYSQL_PWD="teafarm_dev_pwd"
export TEAFARM_MYSQL_HOST="localhost"
export TEAFARM_MYSQL_DB="teafarm_dev_db"

# Set MYSQL_ROOT_PWD based on user input
export MYSQL_ROOT_PWD="$MYSQL_ROOT_PWD"

echo "Environment variables set."

# Execute the SQL setup script
echo "Setting up the database..."
mysql -u root -p"$MYSQL_ROOT_PWD" 2>/dev/null <<EOF
CREATE DATABASE IF NOT EXISTS teafarm_dev_db;
CREATE USER IF NOT EXISTS 'teafarm_dev'@'localhost' IDENTIFIED BY 'teafarm_dev_pwd';
GRANT ALL PRIVILEGES ON teafarm_dev_db.* TO 'teafarm_dev'@'localhost';
FLUSH PRIVILEGES;
EOF

echo "Database setup completed. Kudos!"

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
