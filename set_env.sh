#!/usr/bin/bash

# Prompt user to enter MySQL root password
read -sp "Enter your MySQL root password: " MYSQL_ROOT_PWD
echo # Move to a new line after password input

# Set PYTHONPATH to the current working directory
export FLASK_APP=$PWD/web_dynamic/app.py
export PYTHONPATH=$PWD

export TEAFARM_MYSQL_USER=teafarm_dev
export TEAFARM_MYSQL_PWD=teafarm_dev_pwd
export TEAFARM_MYSQL_HOST=localhost
export TEAFARM_MYSQL_DB=teafarm_dev_db

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

# intall required modules

sudo apt-get update
sudo apt-get install -y pkg-config
sudo apt-get install -y libmysqlclient-dev
sudo apt-get install -y python3-pip
sudo apt-get install -y gunicorn
sudo apt-get install -y python3-pip nginx
sudo apt-get install -y certbot python3-certbot-nginx

sudo pip3 install flask
sudo pip3 install flask_login
sudo pip3 install flask_wtf
sudo pip3 install mysqlclient
sudo pip3 install flask_sqlalchemy
sudo pip3 install Flask-Migrate
sudo pip3 install email_validator
