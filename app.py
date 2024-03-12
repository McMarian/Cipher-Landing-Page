from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from flask import session
from flask import url_for
from flask import redirect

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mydatabase'
mongo = PyMongo(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/coming-soon')
def coming_soon():
    return render_template('coming-soon.html')

@app.route('/price')
def price():
    return render_template('price.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/sign')
def sign():
    return render_template('sign.html')
@app.route('/settings')
def settings():
    return render_template('settings.html')
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    users = mongo.db.users
    existing_user = users.find_one({'username' : username})

    if existing_user is None:
        users.insert({'username' : username, 'password' : password})
        return jsonify({'message': 'User created successfully'}), 200
    else:
        return jsonify({'message': 'User already exists'}), 400

@app.route('/login', methods=['POST'])
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    users = mongo.db.users
    existing_user = users.find_one({'username' : username})

    if existing_user:
        if existing_user['password'] == password:
            session['username'] = username  # Store the username in the session
            return redirect(url_for('profile'))  # Redirect to profile page
        else:
            return jsonify({'message': 'Invalid password'}), 401
    else:
        return jsonify({'message': 'User does not exist'}), 400

if __name__ == '__main__':
    app.run(port=5000, debug=True)