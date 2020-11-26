from flask import Blueprint, jsonify

bp = Blueprint("api", __name__)

@bp.route("/")
def hello():
    return jsonify("One small step for a man...")
