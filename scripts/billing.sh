#!/bin/bash

set -e

# Update & Base Packages
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv postgresql postgresql-contrib libpq-dev curl rabbitmq-server

export BILLING_DB_NAME=${BILLING_DB_NAME}
export BILLING_DB_USER=${BILLING_DB_USER}
export BILLING_DB_PASSWORD=${BILLING_DB_PASSWORD}
export RABBITMQ_USER=${RABBITMQ_USER}
export RABBITMQ_PASSWORD=${RABBITMQ_PASSWORD}
export RABBITMQ_VHOST=${RABBITMQ_VHOST:-/}

# Database Setup
sudo systemctl enable postgresql
sudo systemctl start postgresql
sudo -u postgres psql -c "CREATE DATABASE ${BILLING_DB_NAME};" || true
sudo -u postgres psql -c "CREATE USER ${BILLING_DB_USER} WITH PASSWORD '${BILLING_DB_PASSWORD}';" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${BILLING_DB_NAME} TO ${BILLING_DB_USER};"
sudo -u postgres psql -d ${BILLING_DB_NAME} -c "GRANT ALL ON SCHEMA public TO ${BILLING_DB_USER};"

# RabbitMQ Setup
sudo systemctl enable rabbitmq-server
sudo systemctl start rabbitmq-server
sudo rabbitmq-plugins enable rabbitmq_management
sudo rabbitmqctl add_user "${RABBITMQ_USER}" "${RABBITMQ_PASSWORD}" || true
sudo rabbitmqctl change_password "${RABBITMQ_USER}" "${RABBITMQ_PASSWORD}"
sudo rabbitmqctl set_user_tags "${RABBITMQ_USER}" administrator
sudo rabbitmqctl set_permissions -p "${RABBITMQ_VHOST}" "${RABBITMQ_USER}" ".*" ".*" ".*"

# Node.js & PM2
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install pm2 -g

# App Setup
APP_DIR="/home/vagrant/billing_app"
VENV_DIR="/home/vagrant/venvs/billing_app"
mkdir -p $APP_DIR
mkdir -p "$(dirname "$VENV_DIR")"
chown -R vagrant:vagrant "$(dirname "$VENV_DIR")"
cd $APP_DIR

# Create venv and install
rm -rf "$VENV_DIR"
sudo -u vagrant python3 -m venv "$VENV_DIR"
sudo -u vagrant "$VENV_DIR/bin/pip" install -r requirements.txt

# Start with PM2
sudo -u vagrant pm2 delete billing-api || true
sudo -u vagrant bash -c "cd $APP_DIR && pm2 start server.py --name billing-api --interpreter $VENV_DIR/bin/python3 --update-env"
sudo -u vagrant pm2 save
