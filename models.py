from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, String, Date, DateTime, DECIMAL, Text, Enum, JSON
from sqlalchemy.orm import relationship

db = SQLAlchemy()


#TABLA ROLE
class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
        }
    

#Tabla User

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    rut = db.Column(db.String(12), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    role_id = db.Column(db.Integer, ForeignKey('role.id'), nullable=False)
    registration_date = db.Column(DateTime, default='CURRENT_TIMESTAMP')
    
    role = relationship("Role")

    def serialize(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "rut": self.rut,
            "email": self.email,
            "phone": self.phone,
            "role": self.role.serialize(),
            "registration_date": self.registration_date
        }

# Table Camping 

class Camping(db.Model):
    __tablename__ = 'camping'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    provider_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    rut_del_negocio = db.Column(db.String(12), nullable=False)
    razon_social = db.Column(db.String(100), nullable=False)
    comuna = db.Column(db.String(50), nullable=False)
    region = db.Column(db.String(50), nullable=False)
    telefono = db.Column(db.String(15), nullable=False)
    direccion = db.Column(db.String(255), nullable=False)
    url_web = db.Column(db.String(255), nullable=True)
    url_google_maps = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    rules = db.Column(JSON, nullable=True)  # Cambiado a JSON
    main_image = db.Column(JSON, nullable=True)  # Foto principal en JSON
    images = db.Column(JSON, nullable=True)  # Álbum de imágenes en JSON
    services = db.Column(JSON, nullable=True)  # Servicios en JSON
    provider = relationship("User")
    zones = relationship("Site", back_populates="camping")
    

    def serialize(self):
        return {
            "id": self.id,
            "provider": self.provider.serialize(),
            "name": self.name,
            "rut_del_negocio": self.rut_del_negocio,
            "razon_social": self.razon_social,
            "comuna": self.comuna,
            "region": self.region,
            "telefono": self.telefono,
            "direccion": self.direccion,
            "url_web": self.url_web,
            "url_google_maps": self.url_google_maps,
            "description": self.description,
            "rules": self.rules,  # Cambiado a JSON
            "main_image": self.main_image,
            "images": self.images,
            "services": self.services,
            "zones": [zone.serialize() for zone in self.zones],
            "details": [detail.serialize() for detail in self.details],
        }