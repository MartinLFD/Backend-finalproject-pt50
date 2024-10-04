from flask import Blueprint
from models import Camping
from datetime import datetime
from flask import request, jsonify
from models import db
from auth_utils import view_permission_required
from flask_jwt_extended import (
    jwt_required,
)

camping = Blueprint("camping", __name__ ,url_prefix="/camping")

@camping.route("/", methods=["POST"])
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


@camping.route("/", methods=["GET"])
def get_campings(): 
    campings = Camping.query.all()
    return jsonify([camping.serialize() for camping in campings])


@camping.route("/<int:id>", methods=["DELETE"])
def delete_camping(id):
    camping = Camping.query.get(id)
    if not camping:
        return jsonify({"error": "Camping not found"}), 404
    db.session.delete(camping)
    db.session.commit()
    return jsonify({"message": "Camping deleted"}), 200


@camping.route("/provider/<int:provider_id>/campings", methods=["GET"])
@jwt_required()
@view_permission_required([2])
def get_campings_by_provider(provider_id):
    campings = Camping.query.filter_by(provider_id=provider_id).all()
    if not campings:
        return jsonify({"error": "No campings found for this provider"}), 404
    return jsonify([camping.serialize() for camping in campings]), 200


@camping.route("/provider/<int:provider_id>/camping/<int:camping_id>", methods=["GET"])
def get_camping_before_to_edit(provider_id, camping_id):
    print(f"Fetching camping with provider_id: {provider_id}, camping_id: {camping_id}")

    try:
        camping = Camping.query.filter_by(id=camping_id, provider_id=provider_id).first()
        if not camping:
            print("Camping not found!")
            return jsonify({"error": "Camping not found"}), 404
        
        print(f"Camping found: {camping.serialize()}")
        return jsonify(camping.serialize()), 200
    except Exception as e:
        print(f"Error fetching camping: {e}")
        return jsonify({"error": "Error fetching camping"}), 500


@camping.route('/provider/<int:provider_id>/edit-camping/<int:camping_id>', methods=['PUT'])
def update_camping_for_provider(provider_id, camping_id):
    camping = Camping.query.filter_by(id=camping_id, provider_id=provider_id).first()
    if not camping:
        return jsonify({"error": "Camping not found or doesn't belong to the provider"}), 404

    data = request.get_json()

    try:
        camping.name = data.get('campingName', camping.name)
        camping.razon_social = data.get('razonSocial', camping.razon_social)
        camping.camping_rut = data.get('rut', camping.camping_rut)
        camping.phone = data.get('telefono', camping.phone)
        camping.address = data.get('direccion', camping.address)
        camping.url_web = data.get('paginaWeb', camping.url_web)
        camping.description = data.get('descripcion', camping.description)
        camping.url_google_maps = data.get('googleMaps', camping.url_google_maps)
        camping.landscape = data.get('landscape', camping.landscape)
        camping.type = data.get('type', camping.type)
        camping.comuna = data.get('comuna', camping.comuna)
        camping.region = data.get('region', camping.region)
        camping.rules = data.get('rules', camping.rules)
        camping.images = data.get('images', camping.images)
        camping.services = data.get('services', camping.services)

        db.session.commit()
        return jsonify({"message": "Camping updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error updating camping: {str(e)}"}), 500

@camping.route("/public-view-get-campings", methods=["GET"])
def public_view_get_campings():
    try:
        campings = Camping.query.all()  # Obtén todos los campings
        return jsonify([camping.serialize() for camping in campings]), 200
    except Exception as e:
        print(f"Error al obtener los campings públicos: {e}")
        return jsonify({"error": "Error al obtener los campings públicos"}), 500

