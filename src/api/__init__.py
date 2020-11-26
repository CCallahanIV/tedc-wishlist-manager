from flask import Flask, jsonify

from api.config import Config
from api.routes import bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(bp)

    # Explanation for initializing database in this way:
    # https://flask.palletsprojects.com/en/1.1.x/patterns/appfactories/#factories-extensions
    from api.models import db
    db.init_app(app)

    return app
