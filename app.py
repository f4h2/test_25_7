from flask import Flask
import os
import psycopg2

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    return conn

@app.route('/')
def hello():
    app_name = os.getenv('APP_NAME', 'Default App')
    try:
        conn = get_db_connection()
        conn.close()
        db_status = "Connected to DB"
    except Exception as e:
        db_status = f"DB Error: {str(e)}"
    return f"Hello from Kubernetes! App: {app_name}, DB Status: {db_status}"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)