from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_database(app):
    """
    This function creates all necessary tables in the database.
    Args:
        app (Flask): The Flask application instance.
    Returns:
        None
    """
    # Use the Flask application context
    with app.app_context():
        # Create all tables specified in the SQLAlchemy models
        db.create_all()