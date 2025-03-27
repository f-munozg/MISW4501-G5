from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY

db = SQLAlchemy()

class Provider(db.Model):
    __tablename__ = "providers"

    identification_number = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(255))
    countries = db.Column(ARRAY(db.String), nullable=False)
    identification_number_contact = db.Column(db.String(50), primary_key=True)
    name_contact = db.Column(db.String(200), nullable=False)
    phone_contact = db.Column(db.String(255)) 
    addres_contact = db.Column(db.String(255))