from flask import Blueprint, request, jsonify
from models import User, db
from datetime import datetime
from extensions import bcrypt
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, 
    get_jwt_identity
)

user = Blueprint("user", __name__, url_prefix="/user")

@user.route("/user", methods=["POST"])
def create_user():
    data = request.get_json()
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
    db.session.add(user)
    db.session.commit()
    return jsonify(user.serialize()), 201

@user.route("/login", methods=["POST"])
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
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        "message": "Login successful",
        "token": access_token,
        "refresh_token": refresh_token,
        "user": user.serialize()
    }), 200

# endpoint para refrescar el token usando refresj token previamente importado
@user.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    current_user_id = get_jwt_identity()
    new_token = create_access_token(identity=current_user_id)
    return jsonify({"token": new_token}), 200

@user.route("/user", methods=["GET"])
def get_users(): 
    users = User.query.all()
    return jsonify([user.serialize() for user in users])

@user.route("/user/<int:id>", methods=["DELETE"])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200

@user.route("/user", methods=["PUT"])
@jwt_required()
def update_user():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error:" "user not found"}), 404

    current_password = data.get("current_password")
    if not current_password or not bcrypt.check_password_hash(user.password, current_password):
        return jsonify({"error": "invalid password"}), 401
    
    user.first_name = data.get("first_name", user.first_name)
    user.last_name = data.get("last_name", user.last_name)
    user.phone = data.get("phone", user.phone)

    db.session.commit()
    return jsonify(user.serialize()),200

@user.route("/update_email", methods=["PUT"])
@jwt_required()
def update_email():
    data= request.get_json()
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

@user.route("/update_password", methods=["PUT"])
@jwt_required()
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

@user.route("/update_phone", methods=["PUT"])
@jwt_required()
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
