from flask import Blueprint
from models import Reservation, User
from datetime import datetime
from flask import request, jsonify
from models import db
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

reservation = Blueprint("reservation", __name__ ,url_prefix="/reservation")
@reservation.route("/reservation", methods=["POST"])
def create_reservation():
    try:
        data = request.get_json()

        start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()

        if "reservation_date" not in data or not data["reservation_date"]:
            reservation_date = datetime.now()
        else:
            reservation_date = datetime.strptime(data["reservation_date"], "%Y-%m-%dT%H:%M:%S")

        reservation = Reservation(
            user_id=data["user_id"],
            site_id=data["site_id"],
            start_date=start_date,
            end_date=end_date,
            number_of_people=data["number_of_people"],
            reservation_date=reservation_date,
            selected_services=data.get("selected_services", None),  
            total_amount=data["total_amount"]
        )

        db.session.add(reservation)
        db.session.commit()

        
        return jsonify(reservation.serialize()), 201

    except Exception as e:
        
        return jsonify({"error": str(e)}), 400

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
def delete_reservation(id):
    reservation = Reservation.query.get(id)
    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404
    db.session.delete(reservation)
    db.session.commit()
    return jsonify({"message": "Reservation deleted"}), 200

@reservation.route("/user/<int:user_id>/reservations", methods=["GET"])
@jwt_required()
def get_reservations_by_user_id(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    if not current_user:
        return jsonify({"error": "User not found"}), 404

    if current_user.role_id != 1 and current_user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    reservations = Reservation.query.filter_by(user_id=user_id).all()
    return jsonify([reservation.serialize() for reservation in reservations]), 200