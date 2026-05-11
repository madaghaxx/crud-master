#!/bin/bash
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv curl

# App Setup
APP_DIR="/home/vagrant/api-gateway-app"
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install flask requests pika python-dotenv
pip freeze > requirements.txt

# PM2 Setup
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install pm2 -g
pm2 start "python3 server.py" --name gateway-api