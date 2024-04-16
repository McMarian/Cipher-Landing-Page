from flask import Flask, request, jsonify, render_template, session, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse
from flask_cors import CORS
from sqlalchemy.orm import relationship
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask_wtf import CSRFProtect
import os
from flask_migrate import Migrate

app = Flask(__name__, static_folder='static', template_folder='templates')
app.debug = False
CORS(app)  
csrf = CSRFProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db = SQLAlchemy(app) 
migrate = Migrate(app, db)

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

class User(UserMixin, db.Model):
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    bio = Column(String(500), nullable=True)
    profile_picture = Column(String(500), nullable=True)

    posts = relationship('Post', backref='author', lazy=True)
    comments = relationship('Comment', backref='author', lazy=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/coming-soon')
def coming_soon():
    return render_template('coming-soon.html')

@app.route('/demo')
def demo():
    return render_template('demo.html')

@app.route('/price')
def price():
    return render_template('price.html')

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/profile')
@login_required
def profile():
    from flask_login import current_user
    if current_user.is_authenticated:
        return render_template('profile.html', username=current_user.username)
    else:
        flash('You need to login first.')
        return redirect(url_for('login')) 


@login_manager.unauthorized_handler
def unauthorized():
    # Store the original URL in the session
    session['next'] = request.url
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username and password are required.')
            return redirect(url_for('login'))

        user = User.query.filter_by(username=username).first()

        if user is not None:
            if check_password_hash(user.password, password):
                login_user(user)  # Log the user in
                next_url = session.pop('next', url_for('profile'))  # Default redirect if 'next' is None
                return redirect(next_url)
            else:
                flash('Invalid password.')
                return redirect(url_for('login'))
        else:
            flash('User does not exist.')
            return redirect(url_for('login'))
    else:
        if 'next' not in session:
            session['next'] = url_for('login')
        return render_template('login.html')
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username').strip()  # Remove leading/trailing spaces
        password = request.form.get('password')
        bio = request.form.get('bio')
        profile_picture = request.form.get('profile_picture')

        if not username or not password:
            flash("Username and password can't be empty.")
            return redirect(url_for('signup'))

        existing_user = User.query.filter_by(username=username).first()

        if existing_user is None:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=username, password=hashed_password, bio=bio, profile_picture=profile_picture)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)  # Log the user in
            next_url = session.pop('next', url_for('profile'))  # Default redirect if 'next' is None
            return redirect(next_url)
        else:
            flash('Username already exists.')
            return redirect(url_for('signup'))
    else:
        if 'next' not in session:
            session['next'] = url_for('signup')
        return render_template('signup.html')

# @app.route('/login/google')
# def login_google():
#     callback=url_for('authorized', _external=True)
#     return google.authorize(callback=callback)

# @app.route('/login/google/authorized')
# def google_authorized():
#     resp = google.authorized_response()
#     if resp is None:
#         return f"Access denied: reason={request.args['error_reason']} error={request.args['error_description']}"
#     session['google_token'] = (resp['access_token'], '')
#     me = google.get('userinfo')
#     user = User.query.filter_by(username=me.data['email']).first()
#     if user is None:
#         # Create a new user with the Google account
#         user = User(username=me.data['email'], password='')
#         db.session.add(user)
#         db.session.commit()
#     # Log in the user
#     session['username'] = user.username
#     return redirect(url_for('profile'))

# @google.tokengetter
# def get_google_oauth_token():
#     return session.get('google_token')



@app.route('/posts')
@login_required
def posts():
    posts = Post.query.all()
    return render_template('posts.html', posts=posts)

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