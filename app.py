from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask import Flask, render_template

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
# Configure the connection to the database
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mydatabase'

# Initialize the database with your Flask app
mongo = PyMongo(app)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    # Here you should add the user to the database
    users = mongo.db.users
    existing_user = users.find_one({'username' : username})

    if existing_user is None:
        users.insert({'username' : username, 'password' : password})
        return jsonify({'message': 'User created successfully'}), 200
    else:
        return jsonify({'message': 'User already exists'}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    # Here you should check the user credentials
    users = mongo.db.users
    existing_user = users.find_one({'username' : username})

    if existing_user:
        if existing_user['password'] == password:
            return jsonify({'message': 'Logged in successfully'}), 200
        else:
            return jsonify({'message': 'Invalid password'}), 401
    else:
        return jsonify({'message': 'User does not exist'}), 400

if __name__ == '__main__':
    app.run(port=3000) 
