#!/bin/bash

set -e

# Update & Base Packages
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv curl

# Node.js & PM2
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install pm2 -g

APP_DIR="/home/vagrant/api-gateway-app"
VENV_DIR="/home/vagrant/venvs/api-gateway-app"
mkdir -p $APP_DIR
mkdir -p "$(dirname "$VENV_DIR")"
chown -R vagrant:vagrant "$(dirname "$VENV_DIR")"
cd $APP_DIR

# Create venv and install
rm -rf "$VENV_DIR"
sudo -u vagrant python3 -m venv "$VENV_DIR"
sudo -u vagrant "$VENV_DIR/bin/pip" install -r requirements.txt

# Start with PM2
sudo -u vagrant pm2 delete gateway-api || true
sudo -u vagrant bash -c "cd $APP_DIR && pm2 start server.py --name gateway-api --interpreter $VENV_DIR/bin/python3 --update-env"
sudo -u vagrant pm2 save
