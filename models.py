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
