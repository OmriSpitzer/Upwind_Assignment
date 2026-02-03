from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import mysql.connector
from hashlib import sha224

app = Flask(__name__)
CORS(app)

load_dotenv()
PORT = os.getenv("PORT")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_PORT = os.getenv("MYSQL_PORT")

conn = None
cursor = None

try:
    conn = mysql.connector.connect(
        host=MYSQL_HOST, 
        user=MYSQL_USER, 
        password=MYSQL_PASSWORD, 
        database=MYSQL_DATABASE, 
        port=MYSQL_PORT
        )
    cursor = conn.cursor(dictionary=True)
    print("\n- - - Connected to MySQL - - -\n")
except Exception as e:
    print("Error connecting to MySQL: " + str(e))

def minimize_details(data):
    for item in data:
        item.pop('password')
        item.pop('hash_pass')
    return data

def non_secure_login(username, password):
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    result = cursor.fetchall()
    result = minimize_details(result)
    return {'success': True, 'data': result}

def secure_login(username, password):
    if not username or not password:
        return {'success': False, 'data': "No username or password inserted"}

    try:
        hashed_password = sha224(password.encode()).hexdigest()
        print(f'Hashed password: {hashed_password}')
        query = f"SELECT * FROM users WHERE username = %s AND hash_pass = %s"
        cursor.execute(query, (username, hashed_password))
        result = cursor.fetchall()
        result = minimize_details(result)
        return {'success': True, 'data': result}
    except Exception as e:
        print("Error logging in: " + str(e))
        return {'success': False, 'data': "Error logging in"}

@app.route("/login", methods=["POST"])
def login():
    try:
        username = request.json.get("username")
        password = request.json.get("password")
        isSecure = request.json.get("isSecure")

        print(f"\nLogin request received: {username} {password} {isSecure}")

        result = non_secure_login(username, password) if not isSecure else secure_login(username, password)

        if result['success']:
            data = result['data']
            print(f'Got users: {len(data)}\n')
            return jsonify(response="Login successful", status=200, userData=data)
        else:
            print(f'Error logging in: {data}\n')
            return jsonify(response="Error logging in", status=500)
    except Exception as e:
        print("Error logging in: " + str(e))
        return jsonify(response="Error logging in", status=500)

if __name__ == "__main__":
    app.run(port=PORT, debug=True)
