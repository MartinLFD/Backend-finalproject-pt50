from flask import Blueprint
from models import Review
from datetime import datetime
from flask import request, jsonify
from models import db
from sqlalchemy import func

review = Blueprint("review", __name__ ,url_prefix="/review")

@review.route("/review", methods=["POST"])
def create_review():
    data = request.get_json()
    review = Review(
        user_id=data["user_id"],
        camping_id=data["camping_id"],
        comment=data.get("comment"),
        rating=data["rating"]
    )
    db.session.add(review)
    db.session.commit()
    return jsonify(review.serialize()), 201


#Crear endpoint filtrando por Id de camping
#Investigar query.sum 
@review.route("/get-comments-on-camping/<int:camping_id>/get-review", methods=["GET"])
def get_reviews(camping_id): 
    reviews = Review.query.filter_by(camping_id=camping_id).all()
    
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

@review.route("/get-camping-rating/<int:camping_id>/from-reviews", methods=["GET"])
def get_reviews_by_camping(camping_id):
    reviews = Review.query.filter_by(camping_id=camping_id).all()
    if not reviews:
        return jsonify({"error": "No reviews found for this camping"}), 404
    

    total_reviews = len(reviews)

    total_rating = db.session.query(func.sum(Review.rating)).filter_by(camping_id=camping_id).scalar() or 0

    average_rating = round(total_rating / total_reviews) if total_reviews > 0 else 0 

    reviews_data = [review.serialize() for review in reviews]

    return jsonify({ 
        "reviews": reviews_data,
        "average_rating": average_rating,
        "total_reviews": total_reviews
    }), 200

