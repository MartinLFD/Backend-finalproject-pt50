from flask import Blueprint
from models import Camping
from datetime import datetime
from flask import request, jsonify
from models import db

camping = Blueprint("camping", __name__ ,url_prefix="/camping")

@camping.route('/camping/<int:id>', methods=['GET'], endpoint='get_camping_by_id_unique')
def get_camping_by_id(id):
    try:
        camping = Camping.query.get(id)
        if camping is None:
            return jsonify({"error": "Camping not found"}), 404
        return jsonify(camping.serialize()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@camping.route("/camping", methods=["POST"])

def create_camping():
    data = request.get_json()
    camping = Camping(
        provider_id=data["provider_id"],
        name=data["name"],
        camping_rut=data["camping_rut"],
        razon_social=data["razon_social"],
        comuna=data["comuna"],
        region=data["region"],
        landscape=data.get("landscape"),
        type=data.get("type"),
        phone=data["phone"],
        address=data["address"],
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

@camping.route("/camping/<int:id>", methods=["GET"])
def get_camping_by_id(id):
    camping = Camping.query.get(id)
    return jsonify(camping.serialize()), 200

@camping.route("/camping/<int:id>", methods=["PUT"])
def update_camping(id):
    data = request.get_json()
    camping = Camping.query.get(id)
    if not camping:
        return jsonify({"error": "Camping not found"}), 404
    camping.name = data.get("name", camping.name)
    camping.camping_rut= data.get("camping_rut", camping.camping_rut)
    camping.razon_social = data.get("razon_social", camping.razon_social)
    camping.comuna = data.get("comuna", camping.comuna)
    camping.region = data.get("region", camping.region)
    camping.landscape =  data.get("landscape", camping.landscape)
    camping.type =  data.get("type", camping.type)
    camping.phone = data.get("phone", camping.phone)
    camping.address= data.get("address", camping.address)
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

@camping.route("/provider/<int:provider_id>/campings", methods=["GET"])
def get_campings_by_provider(provider_id):
    campings = Camping.query.filter_by(provider_id=provider_id).all()
    if not campings:
        return jsonify({"error": "No campings found for this provider"}), 404
    return jsonify([camping.serialize() for camping in campings]), 200
