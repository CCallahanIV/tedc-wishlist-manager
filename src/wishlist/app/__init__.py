from flask import Flask, jsonify
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

from app.config import Config
from app.routes import bp


# Initialize extensions, at this point they are not attached to the application.
db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app() -> Flask:
    """Using the `factory` pattern, return an initialized instance of the Flask app that will persist
    for a single request/response lifecycle.

    Returns:
        Flask: instance of the Flask app with registered Blueprints and initialized Database.
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(bp)

    # Explanation for initializing database in this way:
    # https://flask.palletsprojects.com/en/1.1.x/patterns/appfactories/#factories-extensions
    db.init_app(app)
    bcrypt.init_app(app)

    return app
