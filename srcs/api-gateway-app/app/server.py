import os, requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

@app.route('/api/movies', defaults={'path': ''}, methods=['GET', 'POST', 'DELETE'])
@app.route('/api/movies/<path:path>', methods=['GET', 'POST', 'DELETE'])
def proxy_inventory(path):
    url = f"{os.getenv('INVENTORY_API_URL')}/api/movies/{path}"
    resp = requests.request(
        method=request.method,
        url=url,
        headers={key: value for (key, value) in request.headers if key.lower() != 'host'},
        data=request.get_data(),
        params=request.args,
        allow_redirects=False
    )
    return (resp.content, resp.status_code, resp.headers.items())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
