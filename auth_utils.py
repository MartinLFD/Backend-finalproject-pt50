# auth_utils.py

from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask import jsonify
from models import User

def role_required(allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Verificar JWT antes de obtener identidad
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                user = User.query.get(user_id)

                if not user or user.role_id not in allowed_roles:
                    return jsonify({"error": "Acceso no autorizado"}), 403

                return func(*args, **kwargs)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        return wrapper
    return decorator

def view_permission_required(allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Verificar JWT antes de obtener identidad
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                user = User.query.get(user_id)

                if not user or user.role_id not in allowed_roles:
                    return jsonify({"error": "No tienes permiso para ver esta página"}), 403

                return func(*args, **kwargs)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        return wrapper
    return decorator
