#!/bin/bash

# 1. Update & Base Packages
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv postgresql postgresql-contrib libpq-dev curl

# 2. Database Setup
sudo -u postgres psql -c "CREATE DATABASE ${INVENTORY_DB_NAME};" || true
sudo -u postgres psql -c "CREATE USER ${INVENTORY_DB_USER} WITH PASSWORD '${INVENTORY_DB_PASSWORD}';" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${INVENTORY_DB_NAME} TO ${INVENTORY_DB_USER};"
sudo -u postgres psql -d ${INVENTORY_DB_NAME} -c "GRANT ALL ON SCHEMA public TO ${INVENTORY_DB_USER};"

# 3. Node.js & PM2
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install pm2 -g

# 4. App Setup (The Robust Way)
APP_DIR="/home/vagrant/inventory-app"
mkdir -p $APP_DIR
cd $APP_DIR

# Create venv and install directly
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install flask flask-sqlalchemy psycopg2-binary python-dotenv

# Fix requirements visibility
./venv/bin/pip freeze > requirements.txt

# 5. Start PM2 with Absolute Path to avoid "Nothing shown"
# We force PM2 to run inside the 'app' directory
sudo -u vagrant bash -c "cd $APP_DIR/app && pm2 start server.py --name inventory-api --interpreter $APP_DIR/venv/bin/python3"

pm2 save