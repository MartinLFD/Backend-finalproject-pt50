from flask import Blueprint
from models import Camping, Review
from datetime import datetime
from flask import request, jsonify
from models import db
from auth_utils import view_permission_required
from flask_jwt_extended import (
    jwt_required, get_jwt_identity
)
from sqlalchemy import func

camping = Blueprint("camping", __name__, url_prefix="/camping")

@camping.route("/create-camping-by-admin", methods=["POST"])
def create_camping():
    data = request.get_json()
    print("Datos recibidos:", data)  # Este print te ayudará a ver si todos los campos se están enviando correctamente

    # Validar que se reciban los datos obligatorios
    required_fields = ["provider_id", "name", "camping_rut", "razon_social", 
                        "comuna", "region", "phone", "address", "description"]
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"El campo {field} es obligatorio."}), 400

    # Crear el nuevo camping con los datos recibidos
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
        camping.main_image = data.get('main_image', camping.main_image)  # <-- Aquí se maneja main_image como string

        db.session.commit()
        return jsonify({"message": "Camping updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error updating camping: {str(e)}"}), 500

@camping.route("/public-view-get-campings", methods=["GET"])
def public_view_get_campings():
    try:
        # Obtener los parámetros 'limit' y 'offset' de la solicitud (con valores predeterminados)
        limit = int(request.args.get('limit', 10))  # Por defecto, 10 campings por página
        offset = int(request.args.get('offset', 0))  # Por defecto, empezar desde el primero
         
        # Consulta de campings paginada
        campings = Camping.query.offset(offset).limit(limit).all()
        total_campings = Camping.query.count()  # Número total de campings en la base de datos
        
        camping_data_list = []

        for camping in campings:
            total_reviews = db.session.query(func.count(Review.id)).filter_by(camping_id=camping.id).scalar()
            total_rating = db.session.query(func.sum(Review.rating)).filter_by(camping_id=camping.id).scalar() or 0
            average_rating = round(total_rating / total_reviews, 1) if total_reviews > 0 else 0
             
            camping_data = camping.serialize()
            camping_data.update({
                "total_reviews": total_reviews,
                "average_rating": average_rating
            })
            camping_data_list.append(camping_data)

        # Devolver los campings paginados junto con el total de campings
        return jsonify({
            "campings": camping_data_list,
            "total": total_campings,
            "limit": limit,
            "offset": offset
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Error al obtener los campings públicos"}), 500


    
@camping.route("/camping/<int:camping_id>", methods=["GET"]) #GET para traer información de cada camping
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
    


@camping.route('/delete-camping/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_camping(id):
    try:
        # Obtener el ID del usuario logueado
        current_user_id = get_jwt_identity()

        # Buscar el camping por ID
        camping = Camping.query.get(id)

        # Verificar si existe el camping
        if not camping:
            return jsonify({"error": "Camping not found"}), 404

        # Verificar si el usuario es el propietario (provider) del camping
        if camping.provider_id != current_user_id:
            return jsonify({"error": "Unauthorized"}), 403

        # Eliminar el camping si el usuario es el propietario
        db.session.delete(camping)
        db.session.commit()

        return jsonify({"message": "Camping deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@camping.route("/buscar", methods=["POST"])
def buscar_campings():
    data = request.get_json()
    region = data.get("region", "").strip()
    comuna = data.get("comuna", "").strip()

    # Aquí puedes implementar tu lógica para buscar campings
    # Ejemplo: filtrar por región y comuna
    campings = Camping.query.filter(Camping.region == region, Camping.comuna == comuna).all()

    return jsonify([camping.serialize() for camping in campings]), 200
