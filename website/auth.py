from flask import Blueprint, request, render_template, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import os
import random


auth = Blueprint('auth', __name__)


@auth.route("/", methods=['GET', 'POST'])
def login_page():
    """
    Render the login page and handle login requests.
    If the request method is GET and the user is already authenticated, redirect to the home page.
    If the request method is GET and the user is not authenticated, render the login page.
    If the request method is POST, validate the login credentials and log the user in if they are correct.
    Returns:
        If the request method is GET and the user is already authenticated, redirects to the home page.
        If the request method is GET and the user is not authenticated, renders the login page.
        If the request method is POST and the login credentials are correct, redirects to the home page.
        If the request method is POST and the login credentials are incorrect, redirects to the login page with an error message.
        If the request method is POST and the email is not registered, redirects to the login page with an error message.
    """
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect(url_for("views.home"))
        else:
            return render_template("login_page.html", page="Login", user=current_user)
    # If the request method is POST, process the login form
    elif request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        # Query the database for the user
        user = User.query.filter_by(email=email).first()
        # If user exists, check the password
        if user:
            if check_password_hash(user.password, password):
                # If password is correct, log in the user
                flash("Logged in successfully.", category="success")
                login_user(user, remember=True)
                return redirect("/")
            else:
                flash("Incorrect password. Try again.", category="error")
                return redirect("/")
        else:
            # If user does not exist, show an error
            flash("This email has not been registered. Check your spelling.", category="error")
            return redirect("/")


# Route for signing up a new user
@auth.route('/sign-up', methods=['GET', 'POST'])
def signup_page():
    """
    Render the sign-up page and handle sign-up form submission.
    Returns:
        If the request method is GET and the user is authenticated, redirects to the home page.
        If the request method is GET and the user is not authenticated, renders the sign-up page.
        If the request method is POST, processes the sign-up form data and creates a new user.
        Redirects to the login page after successful sign-up.
    """
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect(url_for("views.home"))
        else:
            return render_template("signup_page.html", page="Sign Up", user=current_user)
    elif request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email is already registered.", category="error")
        elif len(first_name) < 2:
            flash("First Name must be greater than 1 character.", category='error')
        elif len(last_name) < 1:
            flash("You must enter a last name.", category="error")
        elif len(email) < 5:
            flash("Email must be greater than 4 characters.", category='error')
            form_first_name = first_name
            form_last_name = last_name
        elif password1 != password2:
            flash("Passwords don't match.", category='error')
            form_first_name = first_name
            form_last_name = last_name
            form_email = email
        elif len(password1) < 7:
            flash("Passwords must be at least 7 characters.", category='error')
            form_first_name = first_name
            form_last_name = last_name
            form_email = email
        else:
            # Create a new user and add it to the database
            new_user = User(email=email, first_name=first_name, last_name=last_name,
                            password=generate_password_hash(password1, method="pbkdf2:sha256"))
            db.session.add(new_user)
            db.session.commit()
            flash("Account created!", category="success")
            flash("You may log in now.", category="primary")
            return redirect(url_for('auth.login_page'))
    return render_template('signup_page.html', page="Sign Up", user=current_user, form_last_name=form_last_name, form_first_name=form_first_name, form_email=form_email)


@auth.route('/logout')
@login_required
def logout():
    """
    Logs out the user and redirects them to the login page.
    Returns:
        A redirect response to the login page.
    """
    logout_user()
    flash("You have been logged out.", category="primary")
    return redirect(url_for('auth.login_page'))


def allowed_file(filename):
    """
    Check if the given filename has a valid extension.
    Args:
        filename (str): The name of the file to check.
    Returns:
        bool: True if the file has a valid extension, False otherwise.
    """
    return "." in filename and filename.rsplit('.', 1)[1].lower() in ["png", 'jpg', 'jpeg']


# Route for removing user profile picture
@auth.route("/edit/profile/<int:id>/remove_profile_picture/", methods=["GET", "POST"])
@login_required
def remove_user_profile_picture(id):
    """
    Remove the profile picture of a user.
    Args:
        id (int): The ID of the user.
    Returns:
        redirect: Redirects back to the previous page.
    Raises:
        None
    """
    user = User.query.get(id)
    path = "website/static/images/" + user.profile_picture
    # Check if the user has a custom profile picture
    if user.profile_picture != "default_profile_photo.jpg":
        if os.path.exists(path):
            os.remove(path)
    # Set the user's profile picture to the default photo
    user.profile_picture = "default_profile_photo.jpg"
    # Update the user in the database
    db.session.add(user)
    db.session.commit()
    flash("Profile photo removed.")
    return redirect(request.referrer)


@auth.route('/edit/profile/<int:id>/images/', methods=['GET', 'POST'])
@login_required
def edit_user_profile_picture(id):
    """
    Edit the user's profile picture.
    Args:
        id (int): The ID of the user.
    Returns:
        redirect: Redirects to the previous page after processing the request.
    Raises:
        None
    """
    if request.method == "GET":
        # Check if the user is accessing their own profile
        if int(id) == current_user.id:
            return render_template("edit_user_profile_picture.html", user=current_user, page="Edit Photo")
        else:
            return redirect("/profile/%s" % id)
    elif request.method == "POST":
        # Check if a file was uploaded
        if 'profile_picture' not in request.files:
            print("Error 1")
            flash("No file was uploaded.", category='error')
            return redirect(request.referrer)
        file = request.files['profile_picture']
        # Check if a file was selected
        if file.filename == "":
            print("Error 2")
            flash("No file was uploaded.", category='error')
            return redirect(request.referrer)
        # Check if the file has a valid extension
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Generate a unique filename to avoid overwriting existing files
            while os.path.exists("website/static/images/" + filename):
                filename = str(random.randint(0, 10000)) + file.filename
            # Save the file to the server
            file.save("website/static/images/" + filename)
            user = User.query.filter_by(id=current_user.id).first()
            try:
                original_pfp = "website/static/images/" + user.profile_picture
                # Check if the user had a custom profile picture
                if original_pfp == "website/static/images/default_profile_photo.jpg":
                    pass
                else:
                    # Remove the original profile picture file
                    if os.path.exists(original_pfp):
                        os.remove(original_pfp)
            except TypeError:
                pass
            # Update the user's profile picture in the database
            user.profile_picture = filename
            db.session.add(user)
            db.session.commit()
        return redirect(request.referrer)


@auth.route('/edit/profile/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user_profile(id):
    """
    Edit the user profile.
    Args:
        id (int): The ID of the user.
    Returns:
        If the request method is GET and the user ID matches the current user's ID, 
        it renders the edit_user_profile.html template with the current user's information.
        If the request method is GET and the user ID does not match the current user's ID,
        it redirects to the profile page of the specified user ID.
        If the request method is POST, it updates the user's profile information based on the form data.
        If the form data is valid, it updates the user's email, first name, last name, bio, and password (if provided).
        Finally, it redirects to the edit profile page.
    """
    if request.method == "GET":
        # Check if the user is accessing their own profile
        if int(id) == current_user.id:
            # Render the edit_user_profile.html template with the current user's information
            return render_template("edit_user_profile.html", user=current_user, page="Settings")
        else:
            # Redirect to the profile page of the specified user ID
            return redirect("/profile/%s" % id)
    elif request.method == "POST":
        # Get the form data
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        old_password = request.form.get("old_password")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        bio = request.form.get('bio')
        user = User.query.filter_by(id=current_user.id).first()
        # Check if the email is already registered
        find_emails = User.query.filter_by(email=email).first()
        # Check if the user is changing their password
        changing_password = True
        if old_password == '' and password1 == '' and password2 == '':
            changing_password = False
        # Validate the form data
        if user.email != email and find_emails != None:
            flash("That email is already registered.", category="error")
        elif len(first_name) < 2:
            flash("First Name must be greater than 1 character.", category='error')
        elif len(email) < 5:
            flash("Email must be greater than 4 characters.", category='error')
        elif len(last_name) < 1:
            flash("You must enter a last name.", category="error")
        elif changing_password and len(password1) < 7:
            flash("Passwords must be at least 7 characters.", category='error')
        elif changing_password and password1 != password2:
            flash("Passwords don't match.", category='error')
        elif changing_password and check_password_hash(user.password, old_password) == False:
            flash("Incorrect original password. Try again.", category="error")
        else:
            # Update the user's information in the database
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.bio = bio
            if changing_password == True:
                # Generate a new password hash if the user is changing their password
                user.password = generate_password_hash(
                    password1, method="pbkdf2:sha256")
            db.session.add(user)
            db.session.commit()
            # Display a success message to the user
            flash("Account updated! Go to your profile to see the changes in action!",
              category="success")
        return redirect("/edit/profile/")
    return render_template("edit_user_profile.html", user=current_user, page="Edit Profile")
