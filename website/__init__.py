from flask_login import LoginManager, current_user
from .database import create_database, db
from flask import Flask, render_template
from .config import Config
from .views import views
from .models import User
from .auth import auth


app = Flask(__name__)
app.config.from_object(Config)
# Initialize SQLAlchemy with this application
db.init_app(app)
# Create all necessary tables in the database
create_database(app)


def create_app():
    """
    This function creates and configures the Flask application.
    Returns:
        app: The configured Flask application.
    """
    app.register_blueprint(views)
    app.register_blueprint(auth)

    login_manager = LoginManager()

    # Specify the name of the login view
    # If a user is not logged in and tries to view a page that requires login,
    # they will be redirected to this view
    login_manager.login_view = 'auth.login_page'

    login_manager.init_app(app)

    @app.errorhandler(404)
    def not_found(e):
        """
        This function renders a custom 404 page and returns a 404 status code.
        Args:
            e (Exception): The exception that was raised.
        Returns:
            A tuple containing the rendered template and the status code.
        """
        return render_template('404.html', user=current_user), 404

    # Register a user loader callback for Flask-Login
    # This callback is used to reload the user object from the user ID stored in the session
    @login_manager.user_loader
    def load_user(id):
        """
        This function retrieves a User object based on the ID.
        Args:
            id (str): The ID of the user.
        Returns:
            User: The User object with the given ID.
        """
        return User.query.get(int(id))

    return app
