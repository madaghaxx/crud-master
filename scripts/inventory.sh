#!/bin/bash
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv postgresql postgresql-contrib libpq-dev curl

# Database Setup
sudo -u postgres psql -c "CREATE DATABASE ${INVENTORY_DB_NAME};" || true
sudo -u postgres psql -c "CREATE USER ${INVENTORY_DB_USER} WITH PASSWORD '${INVENTORY_DB_PASSWORD}';" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${INVENTORY_DB_NAME} TO ${INVENTORY_DB_USER};"
sudo -u postgres psql -d ${INVENTORY_DB_NAME} -c "GRANT ALL ON SCHEMA public TO ${INVENTORY_DB_USER};"

# App Setup
APP_DIR="/home/vagrant/inventory-app"
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install flask flask-sqlalchemy psycopg2-binary python-dotenv
pip freeze > requirements.txt

# PM2 Setup
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install pm2 -g
pm2 start "python3 server.py" --name inventory-api