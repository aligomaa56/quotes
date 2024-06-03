from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Post(db.Model):
    """
    This class represents a Post in the database.

    Attributes:
        id (int): The primary key.
        data (str): The content of the post.
        date (datetime): The date and time the post was created.
        user_id (int): The ID of the user who created the post.
        likes (relationship): The likes associated with the post.
    """
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Text)
    date = db.Column(db.DateTime, default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    likes = db.relationship("Like", backref="post", cascade="all, delete-orphan")

class User(db.Model, UserMixin):
    """
    This class represents a User in the database.

    Attributes:
        id (int): The primary key.
        email (str): The user's email address.
        password (str): The user's password.
        first_name (str): The user's first name.
        last_name (str): The user's last name.
        profile_picture (str): The URL of the user's profile picture.
        posts (relationship): The posts created by the user.
        bio (str): The user's biography.
        links (str): The user's social media links.
        date_joined (datetime): The date and time the user joined.
        likes (relationship): The likes given by the user.
    """
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
    """
    This class represents a Like in the database.

    Attributes:
        id (int): The primary key.
        user_id (int): The ID of the user who gave the like.
        post_id (int): The ID of the post that was liked.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
