from flask import Blueprint, jsonify

bp = Blueprint("api", __name__)

@bp.route("/")
def healthcheck():
    return jsonify("OK"), 200
