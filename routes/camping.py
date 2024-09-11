from flask import Blueprint
from models import Camping
from datetime import datetime
from flask import request, jsonify
from models import db

camping = Blueprint("camping", __name__ ,url_prefix="/camping")

@camping.route("/camping", methods=["POST"])

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

@camping.route("/camping", methods=["GET"])
def get_campings(): 
    campings = Camping.query.all()
    return jsonify([camping.serialize() for camping in campings])

@camping.route("/camping/<int:id>", methods=["PUT"])
def update_camping(id):
    data = request.get_json()
    camping = Camping.query.get(id)
    if not camping:
        return jsonify({"error": "Camping not found"}), 404
    camping.name = data.get("name", camping.name)
    camping.rut_del_negocio = data.get("rut_del_negocio", camping.rut_del_negocio)
    camping.razon_social = data.get("razon_social", camping.razon_social)
    camping.comuna = data.get("comuna", camping.comuna)
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

@camping.route("/camping/<int:id>", methods=["DELETE"])
def delete_camping(id):
    camping = Camping.query.get(id)
    if not camping:
        return jsonify({"error": "Camping not found"}), 404
    db.session.delete(camping)
    db.session.commit()
    return jsonify({"message": "Camping deleted"}), 200