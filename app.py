from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    app_name = os.getenv('APP_NAME', 'Default App')
    api_key = os.getenv('API_KEY', 'No API Key')
    return f"Hello from Kubernetes! App: {app_name}, API Key: {api_key}"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)