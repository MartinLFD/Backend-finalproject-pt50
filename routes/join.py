from flask import Blueprint, request, jsonify
from models import Camping, Site, Reservation
from sqlalchemy import func, and_, or_
from datetime import datetime
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

# Definir el Blueprint
join_bp = Blueprint('join_bp', __name__)

# Ruta para búsqueda de campings y reservas, usando un solo endpoint POST
@join_bp.route('/search', methods=['POST'])
def search_campings():
    """
    Busca campings con sitios disponibles según el destino (comuna o región),
    fechas de check-in y check-out, y el número de personas.
    """
    try:
        # Obtener el cuerpo de la solicitud (JSON body)
        data = request.get_json()
        destination = data.get('destination')  # Puede coincidir con comuna o región
        num_people = data.get('num_people')
        checkin_date = data.get('check_in')
        checkout_date = data.get('check_out')

        # Convertir las fechas de checkin y checkout a formato datetime
        checkin = datetime.strptime(checkin_date, '%Y-%m-%d') if checkin_date else None
        checkout = datetime.strptime(checkout_date, '%Y-%m-%d') if checkout_date else None

        # Imprimir los parámetros recibidos para depuración
        print(f"Búsqueda de camping en: {destination}, Número de personas: {num_people}")
        print(f"Check-in date: {checkin_date}, Check-out date: {checkout_date}")

        # Realizar la consulta en base a destination, num_people, checkin y checkout
        query = db.session.query(Camping).join(Site).outerjoin(Reservation).filter(
            (Camping.region == destination) | (Camping.comuna == destination) if destination else True,
            Site.max_of_people >= num_people if num_people else True,  # Asegurar que el sitio tenga capacidad suficiente
            (Reservation.end_date <= checkin) | (Reservation.end_date.is_(None)) if checkin else True,
            (Reservation.start_date >= checkout) | (Reservation.start_date.is_(None)) if checkout else True,
            Site.status == 'available'  # Filtrar por sitios disponibles
        ).group_by(Camping.id).all()

        # Imprimir la consulta generada para depuración
        print(f"Consulta generada: {query}")

        result = []
        for camping in query:
            available_zones = [
                zone for zone in camping.zones  # Cambiado 'sites' por 'zones'
                if zone.status == 'available'
                and zone.max_of_people >= (num_people if num_people else 0)  # Filtro de número de personas
            ]
            # Imprimir los sitios disponibles por camping
            print(f"Camping ID: {camping.id}, Zonas disponibles: {len(available_zones)}")

            if available_zones:
                result.append({
                    "camping_id": camping.id,
                    "camping_name": camping.name,
                    "region": camping.region,
                    "comuna": camping.comuna,
                    "main_image": camping.main_image,  # Asegúrate de que esto exista en el modelo
                    "description": camping.description,  # Asegúrate de que esto exista en el modelo
                    "reviews_count": len(camping.reviews) if hasattr(camping, 'reviews') else 0,  # Asumiendo que tengas una relación con la tabla de reviews
                    "rating": camping.rating if hasattr(camping, 'rating') else None,  # Asumiendo que tengas una columna de rating
                    "available_zones_count": len(available_zones),
                })

            
        # Imprimir el resultado antes de devolverlo
        print(f"Resultado: {result}")

        return jsonify(result), 200

    except SQLAlchemyError as e:
        print(f"Error en la búsqueda de campings: {str(e)}")
        response = jsonify({"error": "Error en la búsqueda de campings"})
    
        # Añadir encabezados CORS manualmente
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 500