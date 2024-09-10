from flask import Blueprint
from models import Reservation
from datetime import datetime
from flask import request, jsonify
from models import db

reservation = Blueprint("reservation", __name__ ,url_prefix="/reservation")

def create_reservation():
    data = request.get_json()
    reservation = Reservation(
        user_id=data["user_id"],
        site_id=data["site_id"],
        start_date=data["start_date"],
        end_date=data["end_date"],
        number_of_people=data["number_of_people"],
        selected_services=data.get("selected_services"),
        total_amount=data["total_amount"]
    )
    db.session.add(reservation)
    db.session.commit()
    return jsonify(reservation.serialize()), 201

@reservation.route("/reservation", methods=["GET"])
def get_reservations(): 
    reservations = Reservation.query.all()
    return jsonify([reservation.serialize() for reservation in reservations])

@reservation.route("/reservation/<int:id>", methods=["PUT"])
def update_reservation(id):
    data = request.get_json()
    reservation = Reservation.query.get(id)
    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404
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