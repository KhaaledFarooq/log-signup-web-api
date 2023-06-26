#importing the necessary modules
from flask import Flask, request, jsonify, render_template
import jwt
import datetime
import hashlib
import secrets
import os
import psycopg2


#initializing the flask app

app  = Flask('Zelora')

app.secret_key = secrets.token_urlsafe(16)


def get_database_connection():
    mydb = psycopg2.connect(
        host=os.environ.get('DATABASE_HOST'),
        port=os.environ.get('DATABASE_PORT'),
        user=os.environ.get('DATABASE_USER'),
        password=os.environ.get('DATABASE_PASSWORD'),
        database=os.environ.get('DATABASE_NAME')
    )
    return mydb


#Starting app route
@app.route("/", methods=['GET', 'POST'])
def main():
	return render_template("index.html")


@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    # Hashing the password
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    mydb = get_database_connection()
    cursor = mydb.cursor()

    # Check for duplicate username
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        return jsonify({'message': 'Username already exists'}), 400
    
    # Insert the user into the database
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password_hash))
    mydb.commit()

    return jsonify({'message': 'User registered successfully'}), 201



@app.route('/login', methods=['POST'])
def login():

    # get username and password
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    mydb = get_database_connection()
    cursor = mydb.cursor()
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    # Retrieve the user from the database
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if not user or user[1] != password_hash:
        return jsonify({'message': 'Invalid username or password'}), 401

    # Generate an access token
    token = jwt.encode(
        {'username': user[0], 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
        app.secret_key
    )

    return jsonify({'token': token}), 200



@app.route('/protected-page', methods=['GET'])
def protected_page():
    
    # Verify that the access token is provided in the request
    access_token = request.args.get('token')
    if not access_token:
        return jsonify({'message': 'Access token missing'}), 401

    try:
        # decoding token
        decoded_token = jwt.decode(access_token, app.secret_key, algorithms=['HS256'])
        username = decoded_token.get('username')
        if not username:
            return jsonify({'message': 'Invalid access token'}), 401

        protected_data = {'data': 'This is a protected resource for user: ' + username}

        return render_template('protected.html', protected_data=protected_data)

    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Expired access token'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid access token'}), 401


#Running the app
if __name__ =='__main__':
	#app.debug = True
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))