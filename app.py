# app.py
from flask import Flask, jsonify, request  # Importación de jsonify y request para la nueva ruta
from extensions import db, bcrypt, jwt
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import datetime, timedelta, timezone
from sqlalchemy import or_
from routes.role import role
from routes.user import user
from routes.camping import camping
from routes.reservation import reservation
from routes.review import review
from routes.site import site
from models import Site, Camping, Reservation 
from flask_jwt_extended import get_jwt  # evita el loops de peticiones de la funcion  get_jwt 
from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Configura la clave secreta
jwt = JWTManager(app)


# Configuración básica de CORS
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})  # Permite CORS para el frontend

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

# NUEVO: Ruta para búsqueda de sitios
@app.route("/search", methods=["GET"])
def search_sites():
    # Parámetros de búsqueda de la consulta
    region = request.args.get("region")
    comuna = request.args.get("comuna")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    number_of_people = request.args.get("number_of_people", type=int)
    site_type = request.args.get("type")

## MOTOR DE BUSQUEDA USANDO JOIN

    # Filtrar los sitios según los parámetros 
    query = Site.query.join(Camping).filter(Camping.region == region)

    if comuna:
        query = query.filter(Camping.comuna == comuna)

    if start_date and end_date:
        # Convertir las fechas de cadena a formato de fecha datetime
        start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")

        # Filtrar sitios disponibles usando un outerjoin con Reservation
        query = query.outerjoin(Reservation).filter(
            or_(
                Reservation.start_date > end_date_dt,
                Reservation.end_date < start_date_dt,
                Reservation.id.is_(None)  # Para incluir sitios sin reservas
            )
        )

    if number_of_people is not None:
        query = query.filter(Site.max_of_people >= number_of_people, Site.status == 'available')
        
    if site_type:
        query = query.filter(Site.site_type == site_type)

    # Ejecutar la consulta y devolver los resultados
    sites = query.all()

    return jsonify([site.serialize() for site in sites]), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001, debug=True)
