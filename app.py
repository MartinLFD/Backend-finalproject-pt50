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

# ------------------------------------
# CAMPING ENDPOINTS
# ------------------------------------
@app.route("/camping", methods=["POST"])
def create_camping():
    data = request.get_json()
    camping = Camping(
        provider_id=data["provider_id"],
        name=data["name"],
        rut_del_negocio=data["rut_del_negocio"],
        razon_social=data["razon_social"],
        comuna=data["comuna"],
        region=data["region"],
        telefono=data["telefono"],
        direccion=data["direccion"],
        url_web=data.get("url_web"),
        url_google_maps=data.get("url_google_maps"),
        description=data.get("description"),
        rules=data.get("rules"),
        main_image=data.get("main_image"),
        images=data.get("images"),
        services=data.get("services")
    )
    db.session.add(camping)
    db.session.commit()
    return jsonify(camping.serialize()), 201

@app.route("/camping", methods=["GET"])
def get_campings(): 
    campings = Camping.query.all()
    return jsonify([camping.serialize() for camping in campings])

@app.route("/camping/<int:id>", methods=["PUT"])
def update_camping(id):
    data = request.get_json()
    camping = Camping.query.get(id)
    if not camping:
        return jsonify({"error": "Camping not found"}), 404
    camping.name = data.get("name", camping.name)
    camping.rut_del_negocio = data.get("rut_del_negocio", camping.rut_del_negocio)
    camping.razon_social = data.get("razon_social", camping.razon_social)
    camping.comuna_id = data.get("comuna_id", camping.comuna_id)
    camping.region = data.get("region", camping.region)
    camping.telefono = data.get("telefono", camping.telefono)
    camping.direccion = data.get("direccion", camping.direccion)
    camping.url_web = data.get("url_web", camping.url_web)
    camping.url_google_maps = data.get("url_google_maps", camping.url_google_maps)
    camping.description = data.get("description", camping.description)
    camping.rules = data.get("rules", camping.rules)
    camping.main_image = data.get("main_image", camping.main_image)
    camping.images = data.get("images", camping.images)
    camping.services = data.get("services", camping.services)
    db.session.commit()
    return jsonify(camping.serialize()), 200

@app.route("/camping/<int:id>", methods=["DELETE"])
def delete_camping(id):
    camping = Camping.query.get(id)
    if not camping:
        return jsonify({"error": "Camping not found"}), 404
    db.session.delete(camping)
    db.session.commit()
    return jsonify({"message": "Camping deleted"}), 200