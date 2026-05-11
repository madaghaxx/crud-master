import os, requests, pika, json
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

INVENTORY_URL = os.getenv('INVENTORY_API_URL')
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
RABBITMQ_USER = os.getenv('RABBITMQ_USER')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASSWORD')
BILLING_QUEUE = os.getenv('BILLING_QUEUE')

@app.route('/api/movies', defaults={'path': ''}, methods=['GET', 'POST', 'DELETE'])
@app.route('/api/movies/<path:path>', methods=['GET', 'POST', 'DELETE'])
def proxy_inventory(path):
    url = f"{INVENTORY_URL}/api/movies/{path}"
    resp = requests.request(
        method=request.method,
        url=url,
        headers={key: value for (key, value) in request.headers if key.lower() != 'host'},
        data=request.get_data(),
        params=request.args
    )
    return (resp.content, resp.status_code, resp.headers.items())

@app.route('/api/billing', methods=['POST'])
def post_billing():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
        channel = connection.channel()
        channel.queue_declare(queue=BILLING_QUEUE, durable=True)

        channel.basic_publish(exchange='', routing_key=BILLING_QUEUE, body=json.dumps(data), properties=pika.BasicProperties(delivery_mode=2))
        connection.close()
        return jsonify({"message": "Message posted"}), 201 [cite: 1]
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
