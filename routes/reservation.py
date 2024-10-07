from flask import Blueprint
from models import Reservation, User, Site, Camping
from datetime import datetime
from flask import request, jsonify
from models import db
from extensions import bcrypt
from flask_jwt_extended import jwt_required, get_jwt_identity
from auth_utils import view_permission_required

reservation = Blueprint("reservation", __name__, url_prefix="/reservation")

@reservation.route("/reservation", methods=["POST"])
@jwt_required()
def create_reservation():
    data = request.get_json()
    user_id = get_jwt_identity()

    check_in = datetime.strptime(data['check_in'], '%Y-%m-%d')
    check_out = datetime.strptime(data['check_out'], '%Y-%m-%d')

    new_reservation = Reservation(
        user_id=user_id,
        site_id=data["site_id"],
        check_in=check_in,
        check_out=check_out,
        total_price=data["total_price"]
    )
    db.session.add(new_reservation)
    db.session.commit()
    return jsonify({"message": "Reservation created successfully!"}), 201

# Ruta para verificar disponibilidad de un sitio específico
@reservation.route("/check-availability", methods=["POST"])
def check_availability():
    data = request.get_json()
    site_id = data["site_id"]
    check_in = datetime.strptime(data["check_in"], '%Y-%m-%d')
    check_out = datetime.strptime(data["check_out"], '%Y-%m-%d')

    conflicting_reservations = Reservation.query.filter(
        Reservation.site_id == site_id,
        Reservation.check_in < check_out,
        Reservation.check_out > check_in
    ).all()

    if conflicting_reservations:
        return jsonify({"available": False, "message": "Site is not available for the selected dates."}), 200
    else:
        return jsonify({"available": True}), 200