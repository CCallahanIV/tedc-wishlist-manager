from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

from src.routes import bp

def create_app():
    app = Flask(__name__)
    app.config.from_object("src.config.Config")
    app.register_blueprint(bp)

    return app
