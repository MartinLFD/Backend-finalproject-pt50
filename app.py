# app.py
from flask import Flask
from extensions import db, bcrypt, jwt
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import datetime, timedelta, timezone
from routes.role import role
from routes.user import user
from routes.camping import camping
from routes.reservation import reservation
from routes.review import review
from routes.site import site
from flask_jwt_extended import create_access_token, get_jwt_identity, set_access_cookies, get_jwt

app = Flask(__name__)

# Configuraciones
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:iAZHmHoRwXmjcUSvafpcTTZWyugPdSYq@autorack.proxy.rlwy.net:15974/railway'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "super_secret"  # Cambiar en producción
app.config["SECRET_KEY"] = "super_super_secret"
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]  # Usar cookies para tokens
app.config["JWT_ACCESS_COOKIE_PATH"] = "/"  # Ruta de la cookie de acceso
app.config["JWT_COOKIE_SECURE"] = False  # Cambiar a True en producción para usar HTTPS
app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # Deshabilitar CSRF para desarrollo, habilitar en producción
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)  # Duración del token de acceso
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)  # Duración del token de refresco

# Iniciar extensiones
db.init_app(app)
bcrypt.init_app(app)
jwt.init_app(app)
Migrate(app, db)

# Configurar CORS con soporte para credenciales
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

# Middleware para renovar el token JWT automáticamente si está a punto de expirar
@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        # Verificar si el token expira en los próximos 15 minutos
        if datetime.timestamp(now + timedelta(minutes=15)) > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response


# Home
@app.route("/", methods=["GET"])
def home():
    return "<h1>Camping API</h1>"

# ------------------------------------
# ROUTES
# ------------------------------------
# Registrar blueprints
app.register_blueprint(role)
app.register_blueprint(user)
app.register_blueprint(camping)
app.register_blueprint(reservation)
app.register_blueprint(review)
app.register_blueprint(site)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001, debug=True)
