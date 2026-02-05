from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import mysql.connector
from hashlib import sha224

app = Flask(__name__)
CORS(app)

# Load environment variables
load_dotenv()
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_PORT = os.getenv("MYSQL_PORT")

# Database connection variables
conn = None             # Database connection object
cursor = None           # Database cursor object

"""
Connection function to the MySQL database
@return: True if connected successfully, False otherwise
"""
def connect():
    global conn, cursor
    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(
            host=MYSQL_HOST, 
            user=MYSQL_USER, 
            password=MYSQL_PASSWORD, 
            database=MYSQL_DATABASE, 
            port=MYSQL_PORT
        )

        # Create a cursor object to interact with the database
        cursor = conn.cursor(dictionary=True)

        print("\n- - - Connected to MySQL - - -\n")
        return True
    except Exception as e:
        print("Error connecting to MySQL: " + str(e))
        return False

"""
Disconnection function from the MySQL database
@return: True if disconnected successfully, False otherwise
"""
def disconnect():
    global conn, cursor
    try:
        # Close the cursor object
        cursor.close()

        # Close the database connection
        conn.close()

        print("\n- - - Disconnected from MySQL - - -\n")
        return True
    except Exception as e:
        print("Error disconnecting from MySQL: " + str(e))
        return False

"""
Secure login function
@param username: username to login with
@param password: password to login with
@return: dictionary with the success flag and user data
"""
def secure_login(username, password):
    # Empty validation check for username and password
    if not username or not password:
        return {'success': False, 'data': "No username or password inserted"}

    try:
        # Hash the password given
        hashed_password = sha224(password.encode()).hexdigest()

        # Query with parameter placeholders and specific fields to retrieve
        query = f"SELECT country, email, id, name, username FROM users WHERE username = %s AND hash_pass = %s"
        
        # Execute the query with the parameters
        cursor.execute(query, (username, hashed_password))

        # Fetch the result
        result = cursor.fetchall()
        if not result:
            return {'success': False, 'data': "User not found"}
        else:
            return {'success': True, 'data': result}
    except Exception as e:
        # If an error occurs, return the error message
        print("Error logging in: " + str(e))
        return {'success': False, 'data': "Error logging in"}

"""
Non-secure login function
@param username: username to login with
@param password: password to login with
@return: dictionary with the success flag and user data
"""
def non_secure_login(username, password):
    # Simple query
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    
    # Execute the query
    cursor.execute(query)
    
    # Fetch the result
    result = cursor.fetchall()

    if not result:
        return {'success': False, 'data': "User not found"}
    else:
        return {'success': True, 'data': result}

@app.route("/login", methods=["POST"])
def login():
    try:
        # Connect to the MySQL database
        is_connected = connect()
        if not is_connected:
            return jsonify(response="Error connecting to database", status=500)

        # Get variables from the request
        username = request.json.get("username")
        password = request.json.get("password")
        isSecure = request.json.get("isSecure")

        print(f"\nLogin request received:")
        print(f"Username: {username}, Password: {password.replace(password, '*' * len(password))}, Is Secure: {isSecure}")

        # Perform the login depending on the secure mode
        result = non_secure_login(username, password) if not isSecure else secure_login(username, password)

        # Disconnect from the MySQL database
        is_disconnected = disconnect()
        if not is_disconnected:
            return jsonify(response="Error disconnecting from database", status=500)

        # If the login is successful, return the user data
        if result['success']:
            data = result['data']
            print(f'Got users: {len(data)}\n')
            return jsonify(response="Login successful", status=200, userData=data)
        else:
            # If the login is not successful, return the error message
            print(f'Error logging in: {result["data"]}\n')
            return jsonify(response=result["data"], status=500)
    except Exception as e:
        # If an error occurs, return the error message
        print("Error logging in: " + str(e))
        return jsonify(response="Error logging in", status=500)

if __name__ == "__main__":
    app.run(port=8001, debug=True)
