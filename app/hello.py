from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object("app.config.Config")
db = SQLAlchemy(app)


@app.route("/")
def hello():
    return jsonify("One small step for a man...")
