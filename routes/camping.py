from flask import Blueprint, request, jsonify
from models import Camping, Site, db

camping = Blueprint("camping", __name__, url_prefix="/camping")

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

@camping.route('/camping/<int:id>', methods=['GET'])
def get_camping(id):
    camping = Camping.query.get(id)
    if not camping:
        return jsonify({"error": "Camping not found"}), 404
    return jsonify({
        "name": camping.name,
        "razon_social": camping.razon_social,
        "camping_rut": camping.rut,
        "email": camping.email,
        "phone": camping.telefono,
        "address": camping.direccion,
        "precio": camping.precio,
        "url_web": camping.pagina_web,
        "description": camping.descripcion,
        "url_google_maps": camping.google_maps
    })

@camping.route('/camping/<int:id>', methods=['PUT'])
def update_camping(id):
    camping = Camping.query.get(id)
    if not camping:
        return jsonify({"error": "Camping not found"}), 404

    data = request.get_json()

    try:
        camping.name = data.get('campingName', camping.name)
        camping.razon_social = data.get('razonSocial', camping.razon_social)
        camping.rut = data.get('rut', camping.rut)
        camping.email = data.get('email', camping.email)
        camping.telefono = data.get('telefono', camping.telefono)
        camping.direccion = data.get('direccion', camping.direccion)
        camping.precio = data.get('precio', camping.precio)
        camping.pagina_web = data.get('paginaWeb', camping.pagina_web)
        camping.descripcion = data.get('descripcion', camping.descripcion)
        camping.google_maps = data.get('googleMaps', camping.google_maps)

        db.session.commit()
        return jsonify({"message": "Camping updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error updating camping: {str(e)}"}), 500

@camping.route("/search", methods=["POST"])
def search_campings():
    data = request.get_json()
    lugar = data.get("lugar")
    num_personas = data.get("numPersonas")
    tipo = data.get("tipo")

    query = db.session.query(Camping).join(Site).filter(
        Camping.type == tipo, 
        (Camping.region.contains(lugar) | Camping.comuna.contains(lugar)),
        Site.max_of_people >= num_personas
    )

    results = [camping.serialize() for camping in query.all()]
    return jsonify(results)
