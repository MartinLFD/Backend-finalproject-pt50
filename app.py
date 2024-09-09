from flask import Flask, request, jsonify
from models import db
from flask_migrate import Migrate
from flask_cors import CORS
from models import Role, User, Camping, Reservation, Review, Site
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///camping.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
Migrate(app, db)
CORS(app)

# Home
@app.route("/", methods=["GET"])
def home():
    return "<h1>Camping API</h1>"

# ------------------------------------
# ROLE ENDPOINTS
# ------------------------------------
@app.route("/role", methods=["POST"])
def create_role():
    data = request.get_json()
    role = Role(name=data["name"])
    db.session.add(role)
    db.session.commit()
    return jsonify(role.serialize()), 201

@app.route("/role", methods=["GET"])
def get_roles(): 
    roles = Role.query.all()
    return jsonify([role.serialize() for role in roles])

@app.route("/role/<int:id>", methods=["PUT"])
def update_role(id): 
    data = request.get_json()
    role = Role.query.get(id)
    if not role:
        return jsonify({"error": "Role not found"}), 404
    role.name = data.get("name", role.name)
    db.session.commit()
    return jsonify(role.serialize()), 200

@app.route("/role/<int:id>", methods=["DELETE"])
def delete_role(id):
    role = Role.query.get(id)
    if not role:
        return jsonify({"error": "Role not found"}), 404
    db.session.delete(role)
    db.session.commit()
    return jsonify({"message": "Role deleted"}), 200

# ------------------------------------
# USER ENDPOINTS
# ------------------------------------
@app.route("/user", methods=["POST"])
def create_user():
    data = request.get_json()
    user = User(
        first_name=data["first_name"],
        last_name=data["last_name"],
        rut=data["rut"],
        email=data["email"],
        password=data["password"],
        phone=data.get("phone"),
        role_id=data["role_id"],
        registration_date=datetime.now()
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.serialize()), 201

@app.route("/user", methods=["GET"])
def get_users(): 
    users = User.query.all()
    return jsonify([user.serialize() for user in users])

@app.route("/user/<int:id>", methods=["PUT"])
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

@app.route("/user/<int:id>", methods=["DELETE"])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200