#!/bin/bash

# 1. Update and Install System Dependencies
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv postgresql postgresql-contrib libpq-dev curl

# 2. Configure PostgreSQL using your .env keys
DB_NAME=${INVENTORY_DB_NAME}
DB_USER=${INVENTORY_DB_USER}
DB_PASS=${INVENTORY_DB_PASSWORD}

sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;" || true
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# 3. Setup Python Virtual Environment
APP_DIR="/home/vagrant/inventory-app"
cd $APP_DIR

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# 4. Install Node.js and PM2
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install pm2 -g

echo "Inventory VM provisioning complete."