from flask import Flask, request, jsonify
from models import Site
from models import db
from flask import Blueprint

site = Blueprint("site", __name__, url_prefix="/site")

@site.route("/site", methods=["POST"])
def create_site():
    data = request.get_json()
    site = Site(
        name=data["name"],
        campsite_id=data["campsite_id"],
        status=data.get("status", "available"),
        max_of_people=data["max_of_people"],
        price=data["price"],
        facilities=data.get("facilities"),
        dimensions=data.get("dimensions"),
        review=data.get("review", ""),  # New field for review
        url_map_site=data.get("url_map_site", ""),  # New field for map URL
        url_photo_site=data.get("url_photo_site", "")  # New field for photo URL
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
    site.status = data.get("status", site.status)
    site.max_of_people = data.get("max_of_people", site.max_of_people)
    site.price = data.get("price", site.price)
    site.facilities = data.get("facilities", site.facilities)
    site.dimensions = data.get("dimensions", site.dimensions)
    site.review = data.get("review", site.review)  # Update review
    site.url_map_site = data.get("url_map_site", site.url_map_site)  # Update map URL
    site.url_photo_site = data.get("url_photo_site", site.url_photo_site)  # Update photo URL
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
