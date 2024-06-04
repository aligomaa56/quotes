class Config:
    """
    This class contains configuration variables for the Flask application.
    """
    # Secret key for the Flask application. This is used to keep client-side sessions secure.
    SECRET_KEY = 'asdfaskjdfgahet'

    # This disables the feature in Flask-SQLAlchemy that signals the application every time a change is about to be made in the database.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # The database URI that should be used for the connection. Here it's a MySQL database.
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://admin:ADMINadmin123@localhost/quotes"