#!/bin/bash

# Update & Base Packages
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv postgresql postgresql-contrib libpq-dev curl

export INVENTORY_DB_NAME=${INVENTORY_DB_NAME}
export INVENTORY_DB_USER=${INVENTORY_DB_USER}
export INVENTORY_DB_PASSWORD=${INVENTORY_DB_PASSWORD}

# Database Setup
sudo -u postgres psql -c "CREATE DATABASE ${INVENTORY_DB_NAME};" || true
sudo -u postgres psql -c "CREATE USER ${INVENTORY_DB_USER} WITH PASSWORD '${INVENTORY_DB_PASSWORD}';" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${INVENTORY_DB_NAME} TO ${INVENTORY_DB_USER};"
sudo -u postgres psql -d ${INVENTORY_DB_NAME} -c "GRANT ALL ON SCHEMA public TO ${INVENTORY_DB_USER};"

# Node.js & PM2
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install pm2 -g

# App Setup
APP_DIR="/home/vagrant/inventory-app"
mkdir -p $APP_DIR
cd $APP_DIR

# Create venv and install
rm -rf venv
python3 -m venv venv
sudo -u vagrant ./venv/bin/pip install -r requirements.txt

# Start with PM2
sudo -u vagrant pm2 delete inventory-api || true
sudo -u vagrant bash -c "cd $APP_DIR && pm2 start server.py --name inventory-api --interpreter $APP_DIR/venv/bin/python3 --update-env --env /vagrant/.env"
sudo -u vagrant pm2 save