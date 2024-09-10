from flask import Flask, request, jsonify
from models import db
from flask_migrate import Migrate
from flask_cors import CORS
from models import Role, User, Reservation, Review, Site
from datetime import datetime
from routes.camping import camping

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///camping.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
Migrate(app, db)
CORS(app)

# Routes
app.register_blueprint(camping)

# Home
@app.route("/", methods=["GET"])
def home():
    return "<h1>Camping API</h1>"

# ------------------------------------
# ROLE ENDPOINTS
# ------------------------------------
@app.route("/role", methods=["POST"])
def create_role():
    data = request.get_json()
    role = Role(name=data["name"])
    db.session.add(role)
    db.session.commit()
    return jsonify(role.serialize()), 201

@app.route("/role", methods=["GET"])
def get_roles(): 
    roles = Role.query.all()
    return jsonify([role.serialize() for role in roles])

@app.route("/role/<int:id>", methods=["PUT"])
def update_role(id): 
    data = request.get_json()
    role = Role.query.get(id)
    if not role:
        return jsonify({"error": "Role not found"}), 404
    role.name = data.get("name", role.name)
    db.session.commit()
    return jsonify(role.serialize()), 200

@app.route("/role/<int:id>", methods=["DELETE"])
def delete_role(id):
    role = Role.query.get(id)
    if not role:
        return jsonify({"error": "Role not found"}), 404
    db.session.delete(role)
    db.session.commit()
    return jsonify({"message": "Role deleted"}), 200

# ------------------------------------
# USER ENDPOINTS
# ------------------------------------
@app.route("/user", methods=["POST"])
def create_user():
    data = request.get_json()
    user = User(
        first_name=data["first_name"],
        last_name=data["last_name"],
        rut=data["rut"],
        email=data["email"],
        password=data["password"],
        phone=data.get("phone"),
        role_id=data["role_id"],
        registration_date=datetime.now()
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.serialize()), 201

@app.route("/user", methods=["GET"])
def get_users(): 
    users = User.query.all()
    return jsonify([user.serialize() for user in users])

@app.route("/user/<int:id>", methods=["PUT"])
def update_user(id):
    data = request.get_json()
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user.first_name = data.get("first_name", user.first_name)
    user.last_name = data.get("last_name", user.last_name)
    user.rut = data.get("rut", user.rut)
    user.email = data.get("email", user.email)
    user.password = data.get("password", user.password)
    user.phone = data.get("phone", user.phone)
    user.role_id = data.get("role_id", user.role_id)
    db.session.commit()
    return jsonify(user.serialize()), 200

@app.route("/user/<int:id>", methods=["DELETE"])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200

# RESERVATION ENDPOINTS
# ------------------------------------
@app.route("/reservation", methods=["POST"])
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

@app.route("/reservation", methods=["GET"])
def get_reservations(): 
    reservations = Reservation.query.all()
    return jsonify([reservation.serialize() for reservation in reservations])

@app.route("/reservation/<int:id>", methods=["PUT"])
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

@app.route("/reservation/<int:id>", methods=["DELETE"])
def delete_reservation(id):
    reservation = Reservation.query.get(id)
    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404
    db.session.delete(reservation)
    db.session.commit()
    return jsonify({"message": "Reservation deleted"}), 200

# ------------------------------------
# REVIEW ENDPOINTS
# ------------------------------------
@app.route("/review", methods=["POST"])
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

@app.route("/review", methods=["GET"])
def get_reviews(): 
    reviews = Review.query.all()
    return jsonify([review.serialize() for review in reviews])

@app.route("/review/<int:id>", methods=["PUT"])
def update_review(id):
    data = request.get_json()
    review = Review.query.get(id)
    if not review:
        return jsonify({"error": "Review not found"}), 404
    review.comment = data.get("comment", review.comment)
    review.rating = data.get("rating", review.rating)
    db.session.commit()
    return jsonify(review.serialize()), 200

@app.route("/review/<int:id>", methods=["DELETE"])
def delete_review(id):
    review = Review.query.get(id)
    if not review:
        return jsonify({"error": "Review not found"}), 404
    db.session.delete(review)
    db.session.commit()
    return jsonify({"message": "Review deleted"}), 200

# SITE ENDPOINTS
# ------------------------------------
@app.route("/site", methods=["POST"])
def create_site():
    data = request.get_json()
    site = Site(
        name=data["name"],
        campsite_id=data["campsite_id"],
        status=data.get("status", "available"),
        max_of_people=data["max_of_people"],
        price=data["price"],
        facilities=data.get("facilities"),
        dimensions=data.get("dimensions")
    )
    db.session.add(site)
    db.session.commit()
    return jsonify(site.serialize()), 201

@app.route("/site", methods=["GET"])
def get_sites(): 
    sites = Site.query.all()
    return jsonify([site.serialize() for site in sites])

@app.route("/site/<int:id>", methods=["PUT"])
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
    db.session.commit()
    return jsonify(site.serialize()), 200

@app.route("/site/<int:id>", methods=["DELETE"])
def delete_site(id):
    site = Site.query.get(id)
    if not site:
        return jsonify({"error": "Site not found"}), 404
    db.session.delete(site)
    db.session.commit()
    return jsonify({"message": "Site deleted"}), 200

if  __name__ == "__main__": 
    app.run(host= "0.0.0.0", port= 3001, debug= True)
