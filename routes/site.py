from flask import Flask, request, jsonify
from models import Site
from models import Site, db, Camping, Reservation
from flask import Blueprint

site = Blueprint("site", __name__, url_prefix="/site")

@site.route("/site", methods=["POST"])
def create_site():
    data = request.get_json()
    site = Site(
        name=data["name"],
        site_type=data["site_type"],
        camping_id=data["camping_id"], 
        status=data.get("status", "available"),
        max_of_people=data["max_of_people"],
        price=data["price"],
        facilities=data.get("facilities"),
        dimensions=data.get("dimensions"),
        review=data.get("review", ""),  
        url_map_site=data.get("url_map_site", ""),  
        url_photo_site=data.get("url_photo_site", "")  
    )
    db.session.add(site)
    db.session.commit()
    return jsonify(site.serialize()), 201

@site.route("/site", methods=["GET"])
def get_sites(): 
    sites = Site.query.all()
    return jsonify([site.serialize() for site in sites])

@site.route("/site/<int:id>", methods=["PUT"])
def update_site(id):
    data = request.get_json()
    site = Site.query.get(id)
    if not site:
        return jsonify({"error": "Site not found"}), 404
    site.name = data.get("name", site.name)
    site.site_type = data.get("type", site.site_type) # Revisar son 3 tipos
    site.status = data.get("status", site.status)
    site.max_of_people = data.get("max_of_people", site.max_of_people)
    site.price = data.get("price", site.price)
    site.facilities = data.get("facilities", site.facilities)
    site.dimensions = data.get("dimensions", site.dimensions)
    site.review = data.get("review", site.review)  # comentario 
    site.url_map_site = data.get("url_map_site", site.url_map_site)  # foto mapa
    site.url_photo_site = data.get("url_photo_site", site.url_photo_site)  # foto sitio
    db.session.commit()
    return jsonify(site.serialize()), 200

@site.route("/site/<int:id>", methods=["DELETE"])
def delete_site(id):
    site = Site.query.get(id)
    if not site:
        return jsonify({"error": "Site not found"}), 404
    db.session.delete(site)
    db.session.commit()
    return jsonify({"message": "Site deleted"}), 200

@site.route("/<int:camping_id>", methods=["GET"])
def get_reviews_by_camping(camping_id):
    sites = Site.query.filter_by(camping_id=camping_id).all()
    if not sites:  # Cambiado de "site" a "sites" para verificar correctamente
        return jsonify({"error": "No site found for this camping"}), 404
    return jsonify([site.serialize() for site in sites]), 200

@site.route("/site/<int:id>", methods=["GET"])
def get_site_by_id(id):
    site = Site.query.get(id)
    if not site:
        return jsonify({"error": "Site not found"}), 404
    return jsonify(site.serialize()), 200

@site.route('/camping/<int:camping_id>/sites', methods=['GET'])
def get_sites_by_camping(camping_id):
    try:
        sites = Site.query.filter_by(camping_id=camping_id).all()
        return jsonify([site.serialize() for site in sites]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para actualizar el estado de un sitio
@site.route("/update-site/<int:id>/changue-status", methods=["PUT"])
def update_site_status(id):
    try:
        data = request.get_json()
        new_status = data.get("status")
        if new_status not in ["available", "unavailable"]:
            return jsonify({"error": "Estado no válido. Debe ser 'available' o 'unavailable'"}), 400

        site = Site.query.get(id)
        if not site:
            return jsonify({"error": "Sitio no encontrado"}), 404

        site.status = new_status
        db.session.commit()
        return jsonify({"message": "Estado del sitio actualizado", "site": site.serialize()}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta de búsqueda 
@site.route("/search", methods=["GET"])
def search_sites():
    # Parámetros de búsqueda de la consulta
    region = request.args.get("region")
    comuna = request.args.get("comuna")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    number_of_people = request.args.get("number_of_people", type=int)
    site_type = request.args.get("type")

    # Filtrar los sitios según los parámetros del motor de búsqueda
    query = Site.query.join(Camping).filter(Camping.region == region)

    if comuna:
        query = query.filter(Camping.comuna == comuna)
    if start_date and end_date:
        # Lógica para filtrar según la disponibilidad del sitio
        reservations = Reservation.query.filter(
            (Reservation.start_date < end_date) & 
            (Reservation.end_date > start_date)
        ).all()
        reserved_site_ids = [reservation.site_id for reservation in reservations]
        query = query.filter(Site.id.notin_(reserved_site_ids))

    if number_of_people:
        query = query.filter(Site.max_of_people >= number_of_people)
    if site_type:
        query = query.filter(Camping.type == site_type) # Ojo se va quitar type de la tabla Camping. #Revisar

    sites = query.all()

    return jsonify([site.serialize() for site in sites]), 200