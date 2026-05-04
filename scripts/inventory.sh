#!/bin/bash

sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv postgresql postgresql-contrib libpq-dev curl

DB_NAME=${DB_INVENTORY_NAME:-movies_db}
DB_USER=${DB_INVENTORY_USER:-admin}
DB_PASS=${DB_INVENTORY_PASSWORD:-password}

sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;" || true
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';" || true
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

APP_DIR="/home/vagrant/inventory-app"
cd $APP_DIR

python3 -m venv venv
source venv/bin/activate
