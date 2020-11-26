from flask import Flask, jsonify

from src.routes import bp

def create_app():
    app = Flask(__name__)
    app.config.from_object("src.config.Config")
    app.register_blueprint(bp)

    # Explanation for initializing database in this way:
    # https://flask.palletsprojects.com/en/1.1.x/patterns/appfactories/#factories-extensions
    from src.models import db
    db.init_app(app)

    return app
