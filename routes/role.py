from flask import Blueprint
from models import Role
from flask import request, jsonify
from models import db
role = Blueprint("role", __name__ ,url_prefix="/role")
# ------------------------------------
# ROLE ENDPOINTS
# ------------------------------------
@role.route("/role", methods=["POST"])
def create_role():
    data = request.get_json()
    role = Role(name=data["name"])
    db.session.add(role)
    db.session.commit()
    return jsonify(role.serialize()), 201

@role.route("/role", methods=["GET"])
def get_roles(): 
    roles = Role.query.all()
    return jsonify([role.serialize() for role in roles])

@role.route("/role/<int:id>", methods=["PUT"])
def update_role(id): 
    data = request.get_json()
    role = Role.query.get(id)
    if not role:
        return jsonify({"error": "Role not found"}), 404
    role.name = data.get("name", role.name)
    db.session.commit()
    return jsonify(role.serialize()), 200

@role.route("/role/<int:id>", methods=["DELETE"])
def delete_role(id):
    role = Role.query.get(id)
    if not role:
        return jsonify({"error": "Role not found"}), 404
    db.session.delete(role)
    db.session.commit()
    return jsonify({"message": "Role deleted"}), 200