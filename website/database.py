from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_database(app):
    with app.app_context():
        db.create_all()