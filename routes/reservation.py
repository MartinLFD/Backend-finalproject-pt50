from flask import Blueprint
from models import Reservation, User, Site, Camping
from datetime import datetime
from flask import request, jsonify
from models import db
from extensions import bcrypt
from flask_jwt_extended import jwt_required, get_jwt_identity
from auth_utils import view_permission_required


reservation = Blueprint("reservation", __name__, url_prefix="/reservation")
reservation_bp = Blueprint('reservation_bp', __name__)

@reservation.route("/reservation", methods=["POST"])
@jwt_required()
def create_reservation():
    data = request.get_json()
    current_user_id = get_jwt_identity()

    site = Site.query.get(data["site_id"])
    if not site:
        return jsonify({"error": "Site not found"}), 404

    camping = site.camping  

    start_date = datetime.strptime(data["start_date"], '%Y-%m-%d')
    end_date = datetime.strptime(data["end_date"], '%Y-%m-%d')
    num_nights = (end_date - start_date).days

    if num_nights <= 0:
        return jsonify({"error": "End date must be after start date"}), 400

    total_amount = num_nights * site.price

    # Convertir los servicios disponibles a un diccionario para búsqueda rápida
    available_services = {service['name'].lower(): service['price'] for service in camping.services}

    if data.get("selected_services"):
        for service_name in data["selected_services"]:
            service_name_lower = service_name.lower()
            if service_name_lower in available_services:
                total_amount += int(available_services[service_name_lower])  # Asegurarse de que el precio sea un número
            else:
                return jsonify({"error": f"Service '{service_name}' not found in camping services"}), 400

    reservation = Reservation(
        user_id=current_user_id,
        site_id=data["site_id"],
        start_date=start_date,
        end_date=end_date,
        number_of_people=data["number_of_people"],
        selected_services=data.get("selected_services"),  # Guardar solo los nombres de los servicios
        total_amount=total_amount
    )

    db.session.add(reservation)
    db.session.commit()

    return jsonify(reservation.serialize()), 201


@reservation.route("/reservation", methods=["GET"])
@jwt_required()
def get_reservation_for_user():
    id_user_reservation = get_jwt_identity()
    reservations = Reservation.query.filter_by(user_id=id_user_reservation).all()

    return jsonify([reservation.serialize() for reservation in reservations])

@reservation.route("/reservation/<int:id>", methods=["PUT"])
def update_reservation(id):
    data = request.get_json()
    reservation = Reservation.query.get(id)
    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404
    reservation.user_id = data.get("user_id", reservation.user_id)
    reservation.site_id = data.get("site_id", reservation.site_id)
    reservation.start_date = data.get("start_date", reservation.start_date)
    reservation.end_date = data.get("end_date", reservation.end_date)
    reservation.number_of_people = data.get("number_of_people", reservation.number_of_people)
    reservation.selected_services = data.get("selected_services", reservation.selected_services)
    reservation.total_amount = data.get("total_amount", reservation.total_amount)
    db.session.commit()
    return jsonify(reservation.serialize()), 200

@reservation.route("/delete-reservation/<int:id>", methods=["DELETE"])  # Cambié el nombre de la ruta
@jwt_required()
def delete_reservation(id):
    data = request.get_json()
    password = data.get('password')
    
    current_user_id = get_jwt_identity()
    
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Invalid password"}), 401

    reservation = Reservation.query.get(id)
    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404
    
    db.session.delete(reservation)
    db.session.commit()
    
    return jsonify({"message": "Reservation deleted"}), 200


@reservation.route("/view-reservations-customer/<int:user_id>/all-details", methods=["GET"])
@jwt_required()
@view_permission_required([3]) # Solo permite a clientes acceder a sus reservas
def get_reservations_and_details_by_user(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != user_id:
        return jsonify({"error": "No autorizado"}), 403

    try:
 # Obtener todas las reservas del usuario autenticado con detalles relacionados
        reservations = Reservation.query.filter_by(user_id=user_id).all()
        
        if not reservations:
            return jsonify({"error": "No se encontraron reservas para este usuario"}), 404

 # Serializar las reservas y sus detalles utilizando el método serialize
        serialized_reservations = [reservation.serialize() for reservation in reservations]

        return jsonify(serialized_reservations), 200
    
    except Exception as e:
# Imprimir error ????
        print(f"Error en get_reservations_and_details_by_user: {str(e)}")
        return jsonify({"error": "Error interno del servidor", "message": str(e)}), 500


@reservation.route("/reservation-in-camping/<int:provider_id>/reservations", methods=["GET"])
@jwt_required()
@view_permission_required([2])
def get_reservations_by_provider(provider_id):
    try:
        # Llamar a la función del join en join.py
        reservations = get_reservations_with_camping_join(provider_id)
        return jsonify(reservations), 200

    except Exception as e:
        print(f"Error en get_reservations_by_provider: {str(e)}")
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
