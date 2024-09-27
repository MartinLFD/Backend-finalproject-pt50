from flask import Blueprint
from models import Reservation, User, Site
from datetime import datetime
from flask import request, jsonify
from models import db
from extensions import bcrypt
from flask_jwt_extended import jwt_required, get_jwt_identity

reservation = Blueprint("reservation", __name__, url_prefix="/reservation")

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

    if data.get("selected_services"):
        if camping and camping.services:
            for service in data["selected_services"]:
                if service in camping.services:
                    total_amount += camping.services[service]
                else:
                    return jsonify({"error": f"Service '{service}' not found in camping services"}), 400
        else:
            return jsonify({"error": "Camping has no services"}), 400

    reservation = Reservation(
        user_id=current_user_id,
        site_id=data["site_id"],
        start_date=start_date,
        end_date=end_date,
        number_of_people=data["number_of_people"],
        selected_services=data.get("selected_services"),
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

@reservation.route("/reservation/<int:id>", methods=["DELETE"])
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

@reservation.route("/user/<int:user_id>/reservations", methods=["GET"])
@jwt_required()
def get_reservation_by_user(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != user_id:
        return jsonify({"error": "No autorizado"}), 403
    
    # para obtener todas las reservas del usuario authenticado
    reservations = Reservation.query.filter_by(user_id=user_id).all()
    
    if not reservations:
        return jsonify({"error": "No se encontraron reservas para este usuario"}), 404
    
    
    return jsonify([reservation.serialize() for reservation in reservations]), 200