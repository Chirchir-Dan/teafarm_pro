#!/bin/bash

# Function to handle errors
handle_error() {
    echo "An error occurred during the database setup. Check setup_error.log for details."
    if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
        return 1  # Sourced script
    else
        exit 1  # Standalone script
    fi
}

# Prompt user to enter MySQL root password
read -sp "Enter your MySQL root password: " MYSQL_ROOT_PWD
echo # Move to a new line after password input

# Set MYSQL_ROOT_PWD based on user input
export MYSQL_ROOT_PWD="$MYSQL_ROOT_PWD"

echo "Environment variables set."

# Execute the SQL setup script
echo "Setting up the database..."
mysql -u root -p"$MYSQL_ROOT_PWD" 2>setup_error.log <<EOF
CREATE DATABASE IF NOT EXISTS teafarm_dev_db;
CREATE USER IF NOT EXISTS 'teafarm_dev'@'localhost' IDENTIFIED BY 'Te@farm2025!';
GRANT ALL PRIVILEGES ON teafarm_dev_db.* TO 'teafarm_dev'@'localhost';
FLUSH PRIVILEGES;
EOF

# Check if MySQL command was successful
if [ $? -ne 0 ]; then
    handle_error
fi

echo "Database setup completed successfully!"

# Set PYTHONPATH to the current working directory
export FLASK_APP="$PWD/web_dynamic/app.py"
export PYTHONPATH="$PWD"

export TEAFARM_MYSQL_USER="teafarm_dev"
export TEAFARM_MYSQL_PWD="Te@farm2025!"
export TEAFARM_MYSQL_HOST="localhost"
export TEAFARM_MYSQL_DB="teafarm_dev_db"

# Sanity check for environment variables
if [ -z "$FLASK_APP" ] || [ -z "$PYTHONPATH" ] || [ -z "$TEAFARM_MYSQL_USER" ]; then
    echo "Environment variables not set correctly. Exiting."
    handle_error
fi

echo "Environment setup completed. Kudos!"

# Optional: Test database connection
echo "Testing database connection..."
mysql -u "$TEAFARM_MYSQL_USER" -p"$TEAFARM_MYSQL_PWD" -h "$TEAFARM_MYSQL_HOST" -e "USE $TEAFARM_MYSQL_DB;" 2>>setup_error.log
if [ $? -ne 0 ]; then
    echo "Database connection test failed. Check setup_error.log for details."
    handle_error
else
    echo "Database connection test succeeded!"
fi
