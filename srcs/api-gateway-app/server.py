import json
import os

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request
import pika
import requests

dotenv_path = '/vagrant/.env'
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv()
app = Flask(__name__)

EXCLUDED_PROXY_HEADERS = {
    'connection',
    'content-encoding',
    'content-length',
    'date',
    'server',
    'transfer-encoding'
}

INVENTORY_URL = os.getenv('INVENTORY_API_URL')
INVENTORY_PROXY_TIMEOUT = int(os.getenv('INVENTORY_PROXY_TIMEOUT', '10'))
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', '5672'))
RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST', '/')
RABBITMQ_USER = os.getenv('RABBITMQ_USER')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASSWORD')
BILLING_QUEUE = os.getenv('BILLING_QUEUE')

@app.route('/api/movies', defaults={'path': ''}, methods=['GET', 'POST', 'DELETE'])
@app.route('/api/movies/<path:path>', methods=['GET', 'POST', 'DELETE', 'PUT'])
def proxy_inventory(path): 
    suffix = f"/{path}" if path else ""
    url = f"{INVENTORY_URL}/api/movies{suffix}"
    
    try:
        resp = requests.request(
            method=request.method,
            url=url,
            headers={key: value for (key, value) in request.headers if key.lower() != 'host'},
            data=request.get_data(),
            params=request.args,
            timeout=INVENTORY_PROXY_TIMEOUT
        )
        headers = [
            (key, value)
            for key, value in resp.headers.items()
            if key.lower() not in EXCLUDED_PROXY_HEADERS
        ]
        return Response(resp.content, status=resp.status_code, headers=headers)
    except Exception as e:
        return jsonify({"error": f"Gateway could not reach Inventory: {str(e)}"}), 502

@app.route('/api/billing', methods=['POST'])
def post_billing():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                virtual_host=RABBITMQ_VHOST,
                credentials=credentials,
                blocked_connection_timeout=10
            )
        )
        channel = connection.channel()
        channel.queue_declare(queue=BILLING_QUEUE, durable=True)

        channel.basic_publish(
            exchange='', 
            routing_key=BILLING_QUEUE, 
            body=json.dumps(data), 
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
        return jsonify({"message": "Message posted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
