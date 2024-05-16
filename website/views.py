from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_paginate import Pagination, get_page_args
from flask_login import login_required, current_user
from .models import User, Post, Like
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from . import db
import datetime


views = Blueprint('views', __name__)


@views.route('/home/', methods=['GET', 'POST'])
@login_required 
def home():
    if request.method == "POST":
        search_query = request.form.get("search")
        if search_query:
            return redirect(url_for("views.search", search=search_query))
    posts = db.session.query(Post, User).join(User, Post.user_id == User.id).order_by(Post.date.desc()).all()
    return render_template("home.html", user=current_user, page="Home", posts=posts)


@views.route('/profile/')
@login_required
def profile_redirect():
    return redirect('/profile/%s' % current_user.id)


@views.route('/profile/<int:id>', methods=["GET","POST"])
@login_required
def user_profile(id):
    if request.method == "GET":
        user = User.query.get(id)
        posts = Post.query.filter_by(user_id=id).order_by(Post.date.desc()).all()
        name = f"{user.first_name} {user.last_name}"
        date_joined = datetime.datetime.strptime(str(user.date_joined), '%Y-%m-%d %H:%M:%S').strftime('%B %d, %Y')
        return render_template("user_profile.html", page="Your Profile", name=name, user=user, id=id, date_joined=date_joined, posts=posts, current_user=current_user)
    elif request.method == "POST":
        post = request.form.get("post")
        if post is not None:
            new_post = Post(data=post, user_id=current_user.id)
            db.session.add(new_post)
            db.session.commit()
        return redirect(f'/profile/{id}')


@views.route('/edit/profile/')
@login_required
def redirect_to_edit_profile():
    return redirect("/edit/profile/%s" % current_user.id)


@views.route('/post/<int:id>', methods=['GET','POST'])
@login_required
def view_post(id):
    post = Post.query.options(joinedload(Post.user)).get(id)
    if not post:
        return render_template("404.html", error="This post doesn't exist.", current_user=current_user)

    liked = Like.query.filter_by(user=current_user, post=post).first()
    date = str(post.date).split(" ")[0]

    return render_template("view_post.html", page="Post", post=post, liked=liked, date=date)


@views.route('/delete/post/<int:id>')
@login_required
def delete_post(id):
    post = Post.query.get(id)
    if post is None:
        flash("Post not found.", category="error")
        return redirect(url_for("views.home"))
    try:
        if current_user.id == post.user_id:
            db.session.delete(post)
            db.session.commit()
            flash("Post deleted.", category="success")
        else:
            flash("You can only delete your own posts.", category="error")
    except Exception as e:
        flash("An error occurred while deleting the post.", category="error")
        print(e)
    return redirect("/profile/")


@views.route('/search/')
@login_required
def empty_search_handler():
    previous_page = request.referrer
    return redirect(previous_page)


@views.route("/search/<search>", methods=['GET','POST'])
@login_required
def search(search):
    if request.method == "POST":
        if request.form.get("search") != None:
            search = request.form.get('search')
            return redirect("/search/%s" % search)
    else:
        posts = db.session.query(Post, User).join(User, Post.user_id == User.id).filter(
            or_(Post.data.ilike(f"%{search}%"))).all()
        full_name = User.first_name + " " + User.last_name
        if len(search) > 2:
            users = User.query.filter(
                or_(User.first_name.ilike(f"%{search}%"), User.last_name.ilike(f"%{search}%"), full_name.ilike(f"%{search}%"))).all()
        else:
            users = None
        return render_template('search.html', posts=posts, users=users, query=search, user=current_user, current_user=current_user, page="Search")


@views.route('/post/<int:post_id>/like', methods=["POST"])
@login_required
def like_post(post_id):
    previous_page = request.referrer
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user=current_user, post=post).first()
    if like:
        db.session.delete(like)
    else:
        like = Like(user=current_user, post=post)
        db.session.add(like)
    db.session.commit()
    return redirect(previous_page)
