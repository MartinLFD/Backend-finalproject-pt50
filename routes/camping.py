from flask import Blueprint

camping = Blueprint("camping", __name__ ,url_prefix="/camping")

@camping.route("/camping", methods=["GET"])
def home():
    return "<h1>Camping API test</h1>"
