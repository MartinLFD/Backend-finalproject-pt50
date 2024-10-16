from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, String, Date, DateTime, DECIMAL, Text, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from extensions import db
#importación 


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
    camping_rut = db.Column(db.String(12), nullable=False)
    razon_social = db.Column(db.String(100), nullable=False)
    comuna = db.Column(db.String(50), nullable=False)
    region = db.Column(db.String(50), nullable=False)
    landscape = db.Column(db.String(200), nullable = True)
    type = db.Column(db.String(200), nullable = True)
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    url_web = db.Column(db.String(255), nullable=True)
    url_google_maps = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    rules = db.Column(JSON, nullable=True)  
    main_image = db.Column(JSON, nullable=True)  
    images = db.Column(JSON, nullable=True)  
    services = db.Column(JSON, nullable=True)  
    provider = relationship("User")
    zones = relationship("Site", back_populates="camping")
    sites = relationship("Site", back_populates="camping")

    

    def serialize(self):
        return {
            "id": self.id,
            "provider": self.provider.serialize(),
            "name": self.name,
            "camping_rut": self.camping_rut,
            "razon_social": self.razon_social,
            "comuna": self.comuna,
            "region": self.region,
            "landscape": self.landscape,
            "type": self.type,
            "phone": self.phone,
            "address": self.address,
            "url_web": self.url_web,
            "url_google_maps": self.url_google_maps,
            "description": self.description,
            "rules": self.rules,
            "main_image": self.main_image,
            "images": self.images,
            "services": self.services if isinstance(self.services, list) else [],
            "zones": [zone.serialize() for zone in self.zones],
            "site": [Site.serialize() for site in self.site],
        }


    
# Table Reservation
class Reservation(db.Model):
    __tablename__ = 'reservation'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    site_id = db.Column(db.Integer, ForeignKey('site.id'), nullable=False)
    start_date = db.Column(Date, nullable=False)
    end_date = db.Column(Date, nullable=False)
    number_of_people = db.Column(db.Integer, nullable=False)
    reservation_date = db.Column(DateTime, default=datetime.now)
    selected_services = db.Column(JSON, nullable=True)  # Almacenado como lista JSON
    total_amount = db.Column(DECIMAL(10, 2), nullable=False, default=0)

    user = relationship("User")
    site = relationship("Site")

    def serialize(self):
        site = Site.query.get(self.site_id)

        # Extraer solo los nombres de los servicios seleccionados
        selected_services_names = []
        if self.selected_services:
            selected_services_names = self.selected_services  # Simplemente una lista de los nombres

        # Extraer los servicios del camping con nombre y precio (si los servicios están en formato dict)
        camping_services_with_price = []
        if site.camping and isinstance(site.camping.services, dict):
            camping_services_with_price = [{"name": name, "price": price} for name, price in site.camping.services.items()]
        return {
            "id": self.id,
            "user": self.user.serialize(),
            "site": site.serialize(),
            "camping": site.camping.serialize() if site.camping else None,
            "start_date": self.start_date.strftime('%Y-%m-%d'),
            "end_date": self.end_date.strftime('%Y-%m-%d'),
            "number_of_people": self.number_of_people,
            "reservation_date": self.reservation_date.strftime('%Y-%m-%d %H:%M:%S'),
            "selected_services": selected_services_names,  # Solo nombres de los servicios seleccionados
            "total_amount": float(self.total_amount),
            "camping_services_with_price": camping_services_with_price  # Servicios del camping con nombre y precio
        }

    
    
#Table Review
class Review(db.Model):
    __tablename__ = 'review'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    camping_id = db.Column(db.Integer, ForeignKey('camping.id'), nullable=False)
    comment = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)
    
    user = relationship("User")
    camping = relationship("Camping")

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.serialize(),
            "camping": self.camping.serialize(),
            "comment": self.comment,
            "rating": self.rating,
            "date": self.date,
        }
class Site(db.Model): 
    __tablename__ = 'site' 
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    camping_id = db.Column(db.Integer, ForeignKey('camping.id'), nullable=False)
    
    status = db.Column(Enum('available', 'unavailable', name='site_status'), default='available')
    max_of_people = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False, default=10000)
    facilities = db.Column(JSON, nullable=True)
    dimensions = db.Column(JSON, nullable=True)
    review = db.Column(db.Text, nullable=True)  
    url_map_site = db.Column(db.String(255), nullable=True)  
    url_photo_site = db.Column(db.String(255), nullable=True)  
    camping = relationship("Camping", back_populates="zones")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "camping_id": self.camping_id,
            "status": self.status,
            "max_of_people": self.max_of_people,
            "price": self.price,
            "facilities": self.facilities,
            "dimensions": self.dimensions,
            "review": self.review,
            "url_map_site": self.url_map_site,
            "url_photo_site": self.url_photo_site,
            "camping_name": self.camping.name if self.camping else None,  # Nombre del camping asociado
            "camping_services": self.camping.services if self.camping else {},  # Servicios del camping
            "camping_provider": self.camping.provider.serialize() if self.camping else None,  # Información del proveedor
        }