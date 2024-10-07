from flask import Blueprint
from models import Camping, Site, Reservation
from datetime import datetime
from flask import request, jsonify
from models import db
from auth_utils import view_permission_required
from flask_jwt_extended import (
    jwt_required,
)

camping = Blueprint("camping", __name__ ,url_prefix="/camping")

@camping.route("/create-camping-by-admin", methods=["POST"])
def create_camping():
    data = request.get_json()
    print("Datos recibidos:", data)  # Este print te ayudará a ver si todos los datos son correctos
    new_camping = Camping(
        name=data["name"],
        region=data["region"],
        comuna=data["comuna"],
        status=data["status"]
    )
    db.session.add(new_camping)
    db.session.commit()
    return jsonify({"message": "Camping created successfully!"}), 201

# Ruta para buscar campings disponibles
@camping.route("/search", methods=["POST"])
def search_campings():
    data = request.get_json()
    
    # Filtros
    destination = data.get('destination')  # Puede ser región o comuna
    num_people = data.get('num_people')
    check_in = data.get('check_in')
    check_out = data.get('check_out')

    # Convertir check-in y check-out a objetos datetime
    check_in_date = datetime.strptime(check_in, '%Y-%m-%d') if check_in else None
    check_out_date = datetime.strptime(check_out, '%Y-%m-%d') if check_out else None

    # Consulta usando JOIN entre las tablas Camping, Site y Reservation, sin incluir site_type
    query = db.session.query(Camping).join(Site).outerjoin(Reservation).filter(
        (Camping.region == destination) | (Camping.comuna == destination) if destination else True,  # Filtrar por región o comuna
        Site.max_of_people >= num_people if num_people else True,  # Número de personas
        (Reservation.end_date <= check_in_date) | (Reservation.end_date.is_(None)) if check_in_date else True,  # Fechas disponibles
        (Reservation.start_date >= check_out_date) | (Reservation.start_date.is_(None)) if check_out_date else True
    ).all()

    result = []
    for camping in query:
        result.append({
            "camping_name": camping.name,
            "region": camping.region,
            "comuna": camping.comuna,
            "sites": [
                {
                    "site_name": site.name,
                    "max_of_people": site.max_of_people
                } for site in camping.sites
            ]
        })

    return jsonify(result), 200