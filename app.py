from flask import Flask, request, jsonify, render_template, session, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from sqlalchemy.orm import relationship
from authlib.integrations.flask_client import OAuth
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask_wtf import CSRFProtect
import os
oauth = OAuth()

google = oauth.register(
    name='google',
    client_id='your-google-client-id',
    client_secret='your-google-client-secret',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
)
app = Flask(__name__)
CORS(app)  
csrf = CSRFProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db = SQLAlchemy(app) 
oauth = OAuth(app)
class User(db.Model):
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(120), nullable=False)
    posts = relationship('Post', backref='author', lazy=True)

class Post(db.Model):
    id = Column(Integer, primary_key=True)
    content = Column(String(500), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    comments = relationship('Comment', backref='post', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'author': self.author.username
        }

class Comment(db.Model):
    id = Column(Integer, primary_key=True)
    content = Column(String(500), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('post.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'author': self.author.username,
            'post': self.post.id
        }

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
    if 'username' in session:
        return render_template('profile.html', username=session['username'])
    else:
        return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/signup', methods=['POST'])
def signup_post():
    username = request.form.get('username')
    password = request.form.get('password')
    existing_user = User.query.filter_by(username=username).first()

    if existing_user is None:
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        return jsonify({'message': 'User created successfully', 'redirect': url_for('profile', _external=True)})
    else:
        return jsonify({'message': 'User already exists'}), 400

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()

    if user is not None:
        if check_password_hash(user.password, password):
            session['username'] = username
            return jsonify({'message': 'Logged in successfully', 'redirect': url_for('profile', _external=True)})
        else:
            return jsonify({'message': 'Invalid password'}), 401
    else:
        return jsonify({'message': 'User does not exist'}), 400

@app.route('/login/google')
def login_google():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)

@app.route('/login/google/authorized')
def google_authorized():
    resp = google.authorized_response()
    if resp is None:
        return f"Access denied: reason={request.args['error_reason']} error={request.args['error_description']}"
    session['google_token'] = (resp['access_token'], '')
    me = google.get('userinfo')
    user = User.query.filter_by(username=me.data['email']).first()
    if user is None:
        # Create a new user with the Google account
        user = User(username=me.data['email'], password='')
        db.session.add(user)
        db.session.commit()
    # Log in the user
    session['username'] = user.username
    return redirect(url_for('profile'))

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@app.route('/posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    return jsonify([post.to_dict() for post in posts])

@app.route('/posts', methods=['POST'])
def create_post():
    if 'username' not in session:
        return jsonify({'message': 'Not logged in'}), 401

    user = User.query.filter_by(username=session['username']).first()
    content = request.form.get('content')
    post = Post(content=content, author=user)

    db.session.add(post)
    db.session.commit()

    return jsonify(post.to_dict()), 201

@app.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    if 'username' not in session:
        return jsonify({'message': 'Not logged in'}), 401

    post = Post.query.get(post_id)

    if post is None:
        return jsonify({'message': 'Post not found'}), 404

    if post.author.username != session['username']:
        return jsonify({'message': 'Not authorized'}), 403

    content = request.form.get('content')
    if content is not None:
        post.content = content

    db.session.commit()

    return jsonify(post.to_dict()), 200

@app.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    if 'username' not in session:
        return jsonify({'message': 'Not logged in'}), 401

    post = Post.query.get(post_id)

    if post is None:
        return jsonify({'message': 'Post not found'}), 404

    if post.author.username != session['username']:
        return jsonify({'message': 'Not authorized'}), 403

    db.session.delete(post)
    db.session.commit()

    return jsonify({'message': 'Post deleted'}), 200

@app.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    comments = Comment.query.filter_by(post_id=post_id).all()
    return jsonify([comment.to_dict() for comment in comments])

@app.route('/posts/<int:post_id>/comments', methods=['POST'])
def create_comment(post_id):
    if 'username' not in session:
        return jsonify({'message': 'Not logged in'}), 401

    user = User.query.filter_by(username=session['username']).first()
    post = Post.query.get(post_id)

    if post is None:
        return jsonify({'message': 'Post not found'}), 404

    content = request.form.get('content')
    comment = Comment(content=content, author=user, post=post)

    db.session.add(comment)
    db.session.commit()

    return jsonify(comment.to_dict()), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)