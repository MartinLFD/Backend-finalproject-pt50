from flask import Blueprint, request, jsonify
from models import Site, Camping
from models import db
from sqlalchemy.exc import SQLAlchemyError

site = Blueprint("site", __name__, url_prefix="/site")

# Ejemplo de una ruta que obtiene todos los sitios de un camping específico
@site.route("/get-sites-by-camping/<int:camping_id>", methods=["GET"])
def get_sites_by_camping(camping_id):
    try:
        sites = Site.query.filter(Site.camping_id == camping_id).all()
        result = []
        for site in sites:
            result.append({
                "id": site.id,
                "name": site.name,
                "status": site.status,
                "max_of_people": site.max_of_people,
                "price": site.price,
                "facilities": site.facilities,
                "dimensions": site.dimensions,
                "review": site.review,
                "url_map_site": site.url_map_site,
                "url_photo_site": site.url_photo_site
                # Nota: 'site_type' ya no se incluye en los resultados
            })
        return jsonify(result), 200
    except SQLAlchemyError as e:
        print(f"Error al obtener los sitios: {str(e)}")
        return jsonify({"error": "Error al obtener los sitios"}), 500

# Otras rutas y lógica relacionadas con 'Site' pueden seguir aquí, asegurándose de no utilizar 'site_type'