from flask import Flask, request, jsonify
from models import db
from flask_migrate import Migrate
from flask_cors import CORS
from models import Role, User, Reservation, Review, Site
from datetime import datetime
from routes.role import role
from routes.user import user
from routes.camping import camping
from routes.reservation import reservation
from routes.review import review

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///camping.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
Migrate(app, db)
CORS(app)

# Home
@app.route("/", methods=["GET"])
def home():
    return "<h1>Camping API</h1>"



# ------------------------------------
# ROUTES
# ------------------------------------
#ROLE
app.register_blueprint(role)
#USER
app.register_blueprint(user)
#CAMPING
app.register_blueprint(camping)
#RESERVATION
app.register_blueprint(reservation)
#REVIEW
app.register_blueprint(review)





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
