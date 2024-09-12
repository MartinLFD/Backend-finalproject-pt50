from flask import Flask, request, jsonify
from models import db
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import datetime
from routes.role import role
from routes.user import user
from routes.camping import camping
from routes.reservation import reservation
from routes.review import review
from routes.site import site
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///camping.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "super_secret"
app.config["SECRET_KEY"] = "super_super_secret"

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

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
#SITE
app.register_blueprint(site)


if  __name__ == "__main__": 
    app.run(host= "0.0.0.0", port= 3001, debug= True)
