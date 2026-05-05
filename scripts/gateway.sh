#!/bin/bash

sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv curl

APP_DIR="/home/vagrant/api-gateway-app"
cd $APP_DIR

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install pm2 -g

echo "Gateway VM provisioning complete."