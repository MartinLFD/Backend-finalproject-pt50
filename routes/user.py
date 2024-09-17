from flask import Blueprint, request, jsonify
from models import User, db
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token

bcrypt = Bcrypt()
user = Blueprint("user", __name__ ,url_prefix="/user")
# ------------------------------------
# USER ENDPOINTS
# ------------------------------------
@user.route("/user", methods=["POST"])
def create_user():
    data = request.get_json()

     # linea para encriptar la contraseña
    hashed_password = bcrypt.generate_password_hash(data["password"]).decode('utf-8')
    user = User(
        first_name=data["first_name"],
        last_name=data["last_name"],
        rut=data["rut"],
        email=data["email"],
        password=hashed_password,  # se guarda la contraseña encriptada
        phone=data.get("phone"),
        role_id=data["role_id"],
        registration_date=datetime.now()
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.serialize()), 201

@user.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    # buscamos el usuario por email
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # para verificar la contraseña
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401
    
    # si la autenticación es exitosa generar un token JWT
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        "message": "Login successful",
        "token": access_token,
        "user": user.serialize()
    }), 200




@user.route("/user", methods=["GET"])
def get_users(): 
    users = User.query.all()
    return jsonify([user.serialize() for user in users])

@user.route("/user/<int:id>", methods=["PUT"])
def update_user(id):
    data = request.get_json()
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user.first_name = data.get("first_name", user.first_name)
    user.last_name = data.get("last_name", user.last_name)
    user.rut = data.get("rut", user.rut)
    user.email = data.get("email", user.email)
    user.password = data.get("password", user.password)
    user.phone = data.get("phone", user.phone)
    user.role_id = data.get("role_id", user.role_id)
    db.session.commit()
    return jsonify(user.serialize()), 200

@user.route("/user/<int:id>", methods=["DELETE"])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200