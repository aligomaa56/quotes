from flask_login import LoginManager, current_user
from .database import create_database, db
from flask import Flask, render_template
from .config import Config
from .views import views
from .models import User
from .auth import auth


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
create_database(app)


def create_app():
    app.register_blueprint(views)
    app.register_blueprint(auth)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login_page'
    login_manager.init_app(app)


    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html', user=current_user), 404


    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    return app
