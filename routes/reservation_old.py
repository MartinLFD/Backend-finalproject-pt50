from flask import Blueprint, request, jsonify
from models import Camping, Site, Reservation
from datetime import datetime
from models import db
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required
from auth_utils import view_permission_required

camping = Blueprint("camping", __name__, url_prefix="/camping")

@camping.route("/create-camping-by-admin", methods=["POST"])
def create_camping():
    data = request.get_json()
    print("Datos recibidos:", data)  # Este print te ayudará a ver si todos los datos son correctos

    required_fields = ["provider_id", "name", "camping_rut", "razon_social", "comuna", "region", "phone", "address", "description"]
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"El campo {field} es obligatorio."}), 400

    camping = Camping(
        provider_id=data["provider_id"],
        name=data["name"],
        camping_rut=data["camping_rut"],
        razon_social=data["razon_social"],
        comuna=data["comuna"],
        region=data["region"],
        phone=data["phone"],
        address=data["address"],
        url_web=data.get("url_web"),  
        url_google_maps=data.get("url_google_maps"),
        description=data["description"],
        rules=data.get("rules", []),  
        main_image=data.get("main_image"),
        images=data.get("images", []),
        services=data.get("services", []),
    )

    try:
        db.session.add(camping)
        db.session.commit()
        return jsonify(camping.serialize()), 201
    except Exception as e:
        print(f"Error al crear el camping: {e}")
        db.session.rollback()
        return jsonify({"error": "Error interno al crear el camping"}), 500


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
        
        # Aquí agregamos el console log para verificar el valor de los servicios
        print(f"Camping services: {camping.services}")
        
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
    print(f"Main image recibida:{data.get('main_image')}")
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
        camping.main_image = data.get('main_image', camping.main_image)  # <-- Aquí se agrega la main_image

        db.session.commit()
        return jsonify({"message": "Camping updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error updating camping: {str(e)}"}), 500

@camping.route("/search", methods=["POST"])
def search_campings():
    data = request.get_json()
    destination = data.get('destination')
    num_people = data.get('num_people')
    check_in = data.get('check_in')
    check_out = data.get('check_out')

    check_in_date = datetime.strptime(check_in, '%Y-%m-%d') if check_in else None
    check_out_date = datetime.strptime(check_out, '%Y-%m-%d') if check_out else None

    try:
        query = db.session.query(Camping).join(Site).outerjoin(Reservation).filter(
            (Camping.region == destination) | (Camping.comuna == destination) if destination else True,
            Site.max_of_people >= num_people if num_people else True,
            (Reservation.end_date <= check_in_date) | (Reservation.end_date.is_(None)) if check_in_date else True,
            (Reservation.start_date >= check_out_date) | (Reservation.start_date.is_(None)) if check_out_date else True,
            Site.status == 'available'
        ).group_by(Camping.id).all()

        result = []
        for camping in query:
            available_sites = [
                site for site in camping.sites
                if site.status == 'available'
                and site.max_of_people >= num_people
            ]
            result.append({
                "camping_id": camping.id,
                "camping_name": camping.name,
                "region": camping.region,
                "comuna": camping.comuna,
                "available_sites_count": len(available_sites),
            })

        return jsonify(result), 200

    except SQLAlchemyError as e:
        print(f"Error en la búsqueda de campings: {str(e)}")
        return jsonify({"error": "Error en la búsqueda de campings"}), 500

@camping.route("/public-view-get-campings", methods=["GET"])
def public_view_get_campings():
    try:
        campings = Camping.query.all()  # Obtén todos los campings
        return jsonify([camping.serialize() for camping in campings]), 200
    except Exception as e:
        return jsonify({"error": "Error al obtener los campings públicos"}), 500

@camping.route("/camping/<int:camping_id>", methods=["GET"])
def get_public_view_by_camping_id(camping_id):
    try: 
        camping = Camping.query.filter_by(id=camping_id).first()
        if not camping:
            print("Camping not found!")
            return jsonify({"error": "Camping not found"}), 404
        return jsonify(camping.serialize()), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Error al obtener data de camping_id"}), 500
