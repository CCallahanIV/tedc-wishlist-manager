from logging import getLogger
from typing import Dict, List
from uuid import UUID

from flask import Blueprint, jsonify, make_response, request

from app.models import insert_wishlist_entry, list_wishlist_entries, remove_wishlist_entry
from app.models.exceptions import BookNotFound, UserNotFound, WishlistNotFound


bp = Blueprint("api", __name__)
_LOGGER = getLogger(__name__)


def _validate_uuid(value: str) -> str:
    """Validate that a given value is valid UUID.

    Args:
        value (str): Provided candidate string.

    Returns:
        None: Candidate string is a valid UUID.
        str: error response
    """
    try:
        UUID(value)
    except Exception as e:
        _LOGGER.info(f"failed to marshal uuid, exception: {e}")
        return "value for {key} must be valid UUID"


def _validate_payload(
    payload: Dict[str, str],
    required_keys: List[str],
    optional_keys: List[str] = None
) -> str:
    """Validate payload has required keys and that all payload values are valid uuids.

    Args:
        payload (Dict[str, str]): payload received in request
        required_keys (List[str]): List of required key names
        optional_keys (List[str]): List of optional key names

    Returns:
        None: No errors encountered, is valid
        str: We've encountered a validation error and should return it.
    """
    if optional_keys is None:
        optional_keys = []

    # Validate required keys are present
    for key in required_keys:
        if key not in payload:
            return f"missing required key {key}"
    
    # Validate required and optional values valid uuid
    for key in [*required_keys, *optional_keys]:
        val = payload.get(key, None)
        if val is not None and key in payload:
            if (exc := _validate_uuid(val)) is not None:
                return exc.format(key=key)


@bp.route("/")
def healthcheck():
    return jsonify("OK"), 200


@bp.route("/wishlist_entry", methods=["POST", "DELETE"])
def handle_wishlist_entry():
    _LOGGER.debug(f"/wishlist_entry: request received, method: {request.method}")

    if request.method == "POST":
        required_keys = ["book_id", "user_id"]
        optional_keys = ["wishlist_id"]
        payload = request.json

        if (exc := _validate_payload(payload, required_keys, optional_keys=optional_keys)) is not None:
            return exc, 400

        try:
            created_entry = insert_wishlist_entry(**payload)
        except BookNotFound:
            return f"Could not find book for given `book_id`.", 400
        except UserNotFound:
            return f"Could not find user for given `user_id`.", 400
        except Exception:
            _LOGGER.exception("/wishlist_entry: Unhandled exception during entry creation.")
            return "internal server error", 500
        
        _LOGGER.debug("/wishlist_entry: creation complete, formulating response")

        res = make_response(jsonify(created_entry), 201)
        wishlist_id = created_entry["wishlist_id"]
        res.headers["Location"] = f"/wishlist/{wishlist_id}"
        return res
    
    if request.method == "DELETE":
        required_keys = ["wishlist_id", "book_id"]
        payload = request.json

        if (exc := _validate_payload(payload, required_keys)) is not None:
            return exc, 400

        try:
            # Currently, repeated calls to DELETE will always provide a 200, even if the resource
            # doesn't exist. We could potentially perform a check to see if the resource exists and
            # return a 404.
            remove_wishlist_entry(payload["wishlist_id"], payload["book_id"])
            return "OK", 200
        except Exception:
            _LOGGER.exception("/wishlist_entry: Unhandled exception during entry creation.")
            return "internal server error", 500


@bp.route("/wishlist/<string:wishlist_id>", methods=["GET"])
def get_wishlist(wishlist_id):
    _LOGGER.debug("/wishlist: request received")
    
    if (exc := _validate_uuid(wishlist_id)) is not None:
        return exc.format(key="wishlist_id"), 400

    try:
        wishlist = list_wishlist_entries(wishlist_id)
    except WishlistNotFound:
        return "wishlist not found", 404

    return jsonify(wishlist), 200
