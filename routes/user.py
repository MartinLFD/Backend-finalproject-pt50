# user.py

from flask import Blueprint, request, jsonify
from models import User, db
from datetime import datetime
from extensions import bcrypt
from flask_jwt_extended import (
    create_access_token, 
    jwt_required, 
    get_jwt_identity,
    set_access_cookies,
    unset_jwt_cookies
)
from auth_utils import role_required

user = Blueprint("user", __name__, url_prefix="/user")


# obtener usuario:
@user.route("/get-user-test", methods=["GET"])
def get_user():
    try:
        # Obtiene todos los usuarios de la base de datos
        users = User.query.all()

        # Serializa los usuarios y los devuelve como una lista JSON
        users_list = [user.serialize() for user in users]

        return jsonify({
            "status": "success",
            "users": users_list
        }), 200
    except Exception as e:
        # En caso de error, retorna un mensaje de error
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500



# Crear usuario
@user.route("/create-one-user", methods=["POST"])
def create_user():
    data = request.get_json()
    
    # Verificar campos requeridos
    if not all([data.get("first_name"), data.get("last_name"), data.get("rut"), data.get("email"), data.get("password")]):
        return jsonify({"error": "Missing required fields"}), 400

    # Verificar si el email ya está en uso
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already in use"}), 400

    # Verificar si el RUT ya está en uso
    if User.query.filter_by(rut=data["rut"]).first():
        return jsonify({"error": "RUT already in use"}), 400

    # Hashear la contraseña y crear el usuario
    hashed_password = bcrypt.generate_password_hash(data["password"]).decode('utf-8')
    user = User(
        first_name=data["first_name"],
        last_name=data["last_name"],
        rut=data["rut"],
        email=data["email"],
        password=hashed_password,
        phone=data.get("phone"),
        role_id=data["role_id"],
        registration_date=datetime.now()
    )

    # Guardar el usuario en la base de datos
    db.session.add(user)
    db.session.commit()

    return jsonify(user.serialize()), 201


@user.route("/login-user", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401
    
    access_token = create_access_token(identity=user.id)
    user_data = user.serialize()

    response = jsonify({
        "message": "Login successful",
        "user": user_data,
        "token": access_token
    })
    
    set_access_cookies(response, access_token)
    return response, 200

# Logout
@user.route("/logout-user", methods=["POST"])
@jwt_required()
def logout():
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)
    return response, 200

# Obtener información del usuario autenticado
@user.route("/get-authenticated-user", methods=["GET"])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.serialize()), 200

# Actualizar información del usuario (nombres, apellidos)
@user.route("/update-user-info", methods=["PUT"])
@jwt_required()
@role_required([2, 3])  # Permitir a usuarios con role_id 2 (Proveedor) y 3 (Cliente)
def update_user():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    current_password = data.get("current_password")
    if not current_password or not bcrypt.check_password_hash(user.password, current_password):
        return jsonify({"error": "Invalid password"}), 401
    
    user.first_name = data.get("first_name", user.first_name)
    user.last_name = data.get("last_name", user.last_name)
    db.session.commit()
    return jsonify(user.serialize()), 200

# Actualizar correo electrónico
@user.route("/update-user-email", methods=["PUT"])
@jwt_required()
@role_required([2, 3])
def update_email():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    current_password = data.get("current_password")
    new_email = data.get("email")
    if not current_password or not new_email:
        return jsonify({"error": "Current password and new email are required"}), 400

    if not bcrypt.check_password_hash(user.password, current_password):
        return jsonify({"error": "Invalid password"}), 401

    if User.query.filter_by(email=new_email).first():
        return jsonify({"error": "Email already in use"}), 400

    user.email = new_email
    db.session.commit()
    return jsonify({"message": "Email updated successfully"}), 200

# Actualizar contraseña
@user.route("/update-user-password", methods=["PUT"])
@jwt_required()
@role_required([2, 3])
def update_password():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    current_password = data.get("current_password")
    new_password = data.get("new_password")
    if not current_password or not new_password:
        return jsonify({"error": "Current and new passwords are required"}), 400

    if not bcrypt.check_password_hash(user.password, current_password):
        return jsonify({"error": "Invalid current password"}), 401

    hashed_new_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    user.password = hashed_new_password
    db.session.commit()
    return jsonify({"message": "Password updated successfully"}), 200

# Actualizar teléfono
@user.route("/update-user-phone", methods=["PUT"])
@jwt_required()
@role_required([2, 3])
def update_phone():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    current_password = data.get("current_password")
    new_phone = data.get("phone")
    if not current_password or not new_phone:
        return jsonify({"error": "Current password and new phone are required"}), 400

    if not bcrypt.check_password_hash(user.password, current_password):
        return jsonify({"error": "Invalid password"}), 401

    user.phone = new_phone
    db.session.commit()
    return jsonify(user.serialize()), 200
