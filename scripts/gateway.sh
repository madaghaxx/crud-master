#!/bin/bash

# Update & Base Packages
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv curl

# Node.js & PM2
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install pm2 -g

APP_DIR="/home/vagrant/api-gateway-app"
mkdir -p $APP_DIR
cd $APP_DIR

# Create venv and install
rm -rf venv
python3 -m venv venv
sudo -u vagrant ./venv/bin/pip install -r requirements.txt

# Start with PM2
sudo -u vagrant pm2 delete gateway-api || true
sudo -u vagrant bash -c "cd $APP_DIR && pm2 start server.py --name gateway-api --interpreter $APP_DIR/venv/bin/python3 --update-env --env /vagrant/.env"
sudo -u vagrant pm2 save