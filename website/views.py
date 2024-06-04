from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import User, Post, Like
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from . import db
import datetime


# Define the views blueprint
views = Blueprint('views', __name__)


# Define a route for the home page
@views.route('/home/', methods=['GET', 'POST'])
@login_required 
def home():
    """
    Renders the home page of the website.
    If the request method is POST, it checks for a search query in the form data.
    If a search query is provided, it redirects to the search page.
    Otherwise, it retrieves all posts from the database and renders the home.html template.
    Returns:
        The rendered home.html template with the current user and retrieved posts.
    """
    if request.method == "POST":
        # Get the search query from the form
        search_query = request.form.get("search")
        if search_query:
            return redirect(url_for("views.search", search=search_query))
    # Retrieve all posts from the database, along with the associated user information
    posts = db.session.query(Post, User).join(User, Post.user_id == User.id).order_by(Post.date.desc()).all()
    return render_template("home.html", user=current_user, page="Home", posts=posts)


# Define a route for the profile page
@views.route('/profile/')
@login_required
def profile_redirect():
    """
    Redirects to the profile page of the current user.
    Returns:
        A redirect response to the profile page.
    """
    return redirect('/profile/%s' % current_user.id)


@views.route('/profile/<int:id>', methods=["GET","POST"])
@login_required
def user_profile(id):
    """
    Renders the profile page of a specific user.
    If the request method is GET, it retrieves the user information and posts from the database and renders the user_profile.html template.
    If the request method is POST, it checks for a new post in the form data and adds it to the database.
    Args:
        id: The ID of the user.
    Returns:
        The rendered user_profile.html template with the user information and posts.
    """
    if request.method == "GET":
        # Retrieve user information and posts from the database
        user = User.query.get(id)
        posts = Post.query.filter_by(user_id=id).order_by(Post.date.desc()).all()
        name = f"{user.first_name} {user.last_name}"
        date_joined = datetime.datetime.strptime(str(user.date_joined), '%Y-%m-%d %H:%M:%S').strftime('%B %d, %Y')
        return render_template("user_profile.html", page="Your Profile", name=name, user=user, id=id, date_joined=date_joined, posts=posts, current_user=current_user)
    elif request.method == "POST":
        # Check for a new post in the form data and add it to the database
        post = request.form.get("post")
        if post is not None:
            new_post = Post(data=post, user_id=current_user.id)
            db.session.add(new_post)
            db.session.commit()
        return redirect(f'/profile/{id}')


# Define a route for redirecting to the edit profile page
@views.route('/edit/profile/')
@login_required
def redirect_to_edit_profile():
    """
    Redirects to the edit profile page of the current user.
    Returns:
        A redirect response to the edit profile page.
    """
    return redirect("/edit/profile/%s" % current_user.id)


# Define a route for viewing a specific post
@views.route('/post/<int:id>', methods=['GET','POST'])
@login_required
def view_post(id):
    """
    Renders the view post page for a specific post.
    If the request method is GET, it retrieves the post information and renders the view_post.html template.
    If the request method is POST, it checks for a like or unlike action in the form data and updates the like status in the database.
    Args:
        id: The ID of the post.
    Returns:
        The rendered view_post.html template with the post information.
    """
    # Retrieve the post information from the database
    post = Post.query.options(joinedload(Post.user)).get(id)
    if not post:
        return render_template("404.html", error="This post doesn't exist.", current_user=current_user)

    liked = Like.query.filter_by(user=current_user, post=post).first()
    # Extract the date from the post and format it
    date = str(post.date).split(" ")[0]
    return render_template("view_post.html", page="Post", post=post, liked=liked, date=date)


# Define a route for deleting a post
@views.route('/delete/post/<int:id>')
@login_required
def delete_post(id):
    """
    Delete a post with the given ID.
    Args:
        id (int): The ID of the post to be deleted.
    Returns:
        redirect: Redirects to the user's profile page.
    Raises:
        None
    """
    # Retrieve the post from the database
    post = Post.query.get(id)
    if post is None:
        flash("Post not found.", category="error")
        return redirect(url_for("views.home"))
    try:
        # Check if the current user is the owner of the post
        if current_user.id == post.user_id:
            # Delete the post from the database
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
    """
    Redirects the user to the previous page.
    This function is used as a handler for the '/search/' route. It redirects the user to the previous page they were on.
    Returns:
        redirect: A redirect response to the previous page.
    """
    previous_page = request.referrer
    return redirect(previous_page)


@views.route("/search/<search>", methods=['GET','POST'])
@login_required
def search(search):
    """
    Search function to handle search requests.
    Args:
        search (str): The search query.
    Returns:
        render_template: The rendered search.html template with search results.
    """
    if request.method == "POST":
        if request.form.get("search") != None:
            search = request.form.get('search')
            return redirect("/search/%s" % search)
    else:
        # Retrieve posts that match the search query
        posts = db.session.query(Post, User).join(User, Post.user_id == User.id).filter(
            or_(Post.data.ilike(f"%{search}%"))).all()
        full_name = User.first_name + " " + User.last_name
        if len(search) > 2:
            # Retrieve users that match the search query
            users = User.query.filter(
                or_(User.first_name.ilike(f"%{search}%"), User.last_name.ilike(f"%{search}%"), full_name.ilike(f"%{search}%"))).all()
        else:
            users = None
        return render_template('search.html', posts=posts, users=users, query=search, user=current_user, current_user=current_user, page="Search")


@views.route('/post/<int:post_id>/like', methods=["POST"])
@login_required
def like_post(post_id):
    """
    Like or unlike a post.
    Args:
        post_id (int): The ID of the post to like or unlike.
    Returns:
        redirect: Redirects the user to the previous page after the like/unlike operation.
    """
    # Get the previous page URL
    previous_page = request.referrer

    post = Post.query.get_or_404(post_id)
    # Check if the user has already liked the post
    like = Like.query.filter_by(user=current_user, post=post).first()
    if like:
        db.session.delete(like)
    else:
        like = Like(user=current_user, post=post)
        db.session.add(like)
    db.session.commit()
    return redirect(previous_page)
