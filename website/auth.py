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
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect(url_for("views.home"))
        else:
            return render_template("login_page.html", page="Login", user=current_user)
    elif request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in successfully.", category="success")
                login_user(user, remember=True)
                return redirect("/")
            else:
                flash("Incorrect password. Try again.", category="error")
                return redirect("/")
        else:
            flash(
                "This email has not been registered. Check your spelling.", category="error")
            return redirect("/")


@auth.route('/sign-up', methods=['GET', 'POST'])
def signup_page():
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
    logout_user()
    flash("You have been logged out.", category="primary")
    return redirect(url_for('auth.login_page'))


def allowed_file(filename):
    return "." in filename and filename.rsplit('.', 1)[1].lower() in ["png", 'jpg', 'jpeg']


@auth.route("/edit/profile/<int:id>/remove_profile_picture/", methods=["GET", "POST"])
@login_required
def remove_user_profile_picture(id):
    user = User.query.get(id)
    path = "website/static/profile_pictures/" + user.profile_picture
    if user.profile_picture != "default_profile_photo.jpg":
        if os.path.exists(path):
            os.remove(path)
    user.profile_picture = "default_profile_photo.jpg"
    db.session.add(user)
    db.session.commit()
    flash("Profile photo removed.")
    return redirect(request.referrer)


@auth.route('/edit/profile/<int:id>/profile_picture/', methods=['GET', 'POST'])
@login_required
def edit_user_profile_picture(id):
    if request.method == "GET":
        if int(id) == current_user.id:
            return render_template("edit_user_profile_picture.html", user=current_user, page="Edit Photo")
        else:
            return redirect("/profile/%s" % id)
    elif request.method == "POST":
        if 'profile_picture' not in request.files:
            print("Error 1")
            flash("No file was uploaded.", category='error')
            return redirect(request.referrer)
        file = request.files['profile_picture']
        if file.filename == "":
            print("Error 2")
            flash("No file was uploaded.", category='error')
            return redirect(request.referrer)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            while os.path.exists("website/static/profile_pictures/" + filename):
                filename = str(random.randint(0, 10000)) + file.filename
            file.save("website/static/profile_pictures/" + filename)
            user = User.query.filter_by(id=current_user.id).first()
            try:
                original_pfp = "website/static/profile_pictures/" + user.profile_picture
                if original_pfp == "website/static/profile_pictures/default_profile_photo.jpg":
                    pass
                else:
                    if os.path.exists(original_pfp):
                        os.remove(original_pfp)
            except TypeError:
                pass
            user.profile_picture = filename
            db.session.add(user)
            db.session.commit()
        return redirect(request.referrer)


@auth.route('/edit/profile/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user_profile(id):
    if request.method == "GET":
        if int(id) == current_user.id:
            return render_template("edit_user_profile.html", user=current_user, page="Settings")
        else:
            return redirect("/profile/%s" % id)
    elif request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        old_password = request.form.get("old_password")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        bio = request.form.get('bio')
        user = User.query.filter_by(id=current_user.id).first()
        find_emails = User.query.filter_by(email=email).first()
        changing_password = True
        if old_password == '' and password1 == '' and password2 == '':
            changing_password = False
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
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.bio = bio
            if changing_password == True:
                user.password = generate_password_hash(
                    password1, method="pbkdf2:sha256")
            db.session.add(user)
            db.session.commit()
            flash("Account updated! Go to your profile to see the changes in action!",
                  category="success")
        return redirect("/edit/profile/")
    return render_template("edit_user_profile.html", user=current_user, page="Edit Profile")
