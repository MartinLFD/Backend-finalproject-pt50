from flask import Blueprint
from models import Review
from datetime import datetime
from flask import request, jsonify
from models import db

review = Blueprint("review", __name__ ,url_prefix="/review")

@review.route("/review", methods=["POST"])
def create_review():
    data = request.get_json()
    review = Review(
        user_id=data["user_id"],
        campsite_id=data["campsite_id"],
        comment=data.get("comment"),
        rating=data["rating"]
    )
    db.session.add(review)
    db.session.commit()
    return jsonify(review.serialize()), 201

@review.route("/review", methods=["GET"])
def get_reviews(): 
    reviews = Review.query.all()
    return jsonify([review.serialize() for review in reviews])

@review.route("/review/<int:id>", methods=["PUT"])
def update_review(id):
    data = request.get_json()
    review = Review.query.get(id)
    if not review:
        return jsonify({"error": "Review not found"}), 404
    review.comment = data.get("comment", review.comment)
    review.rating = data.get("rating", review.rating)
    db.session.commit()
    return jsonify(review.serialize()), 200

@review.route("/review/<int:id>", methods=["DELETE"])
def delete_review(id):
    review = Review.query.get(id)
    if not review:
        return jsonify({"error": "Review not found"}), 404
    db.session.delete(review)
    db.session.commit()
    return jsonify({"message": "Review deleted"}), 200
