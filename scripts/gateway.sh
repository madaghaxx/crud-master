#!/bin/bash

# 1. Update & Base Packages
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv curl

# 2. Node.js & PM2
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install pm2 -g

# 3. App Setup
APP_DIR="/home/vagrant/api-gateway-app"
mkdir -p $APP_DIR
cd $APP_DIR

# Create venv and install
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install flask requests pika python-dotenv

# Fix requirements visibility
./venv/bin/pip freeze > requirements.txt

# 4. Start PM2 with Absolute Path
sudo -u vagrant bash -c "cd $APP_DIR/app && pm2 start server.py --name gateway-api --interpreter $APP_DIR/venv/bin/python3"

pm2 save