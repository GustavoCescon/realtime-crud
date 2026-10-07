from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity


def roles_required(*allowed_roles: str):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get("role")

            if user_role not in allowed_roles:
                return jsonify({
                    "error": "forbidden",
                    "message": "You do not have permission to perform this action.",
                }), 403

            return function(*args, **kwargs)

        return wrapper

    return decorator

def owner_or_roles_required(*allowed_roles: str):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            current_user_id = get_jwt_identity()

            user_id = kwargs.get("user_id")

            is_allowed_role = claims.get("role") in allowed_roles
            is_owner = current_user_id == str(user_id)

            if not is_allowed_role and not is_owner:
                return jsonify({
                    "error": "forbidden",
                    "message": "You do not have permission to perform this action.",
                }), 403

            return function(*args, **kwargs)

        return wrapper

    return decorator
