from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Text)
    date = db.Column(db.DateTime, default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    likes = db.relationship("Like", backref="post", cascade="all, delete-orphan")

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    profile_picture = db.Column(db.String(1000), default="default_profile_photo.jpg")
    posts = db.relationship("Post", backref='user', cascade='all, delete-orphan')
    bio = db.Column(db.String(1500))
    links = db.Column(db.String(500))
    date_joined = db.Column(db.DateTime, default=func.now())
    likes = db.relationship("Like", backref="user", cascade="all, delete-orphan")

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
