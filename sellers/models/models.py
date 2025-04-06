from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Float
from sqlalchemy.dialects.postgresql import ARRAY, UUID
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    email = Column(String(50), nullable=False)
    role = Column(UUID(as_uuid=True), ForeignKey('roles.id'), nullable=False)

class Seller(db.Model):
    __tablename__ = "sellers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    identification_number = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False, unique=True)
    email = Column(String(255), nullable=False)
    address = Column(String(255))
    phone = Column(String(255)) 
    zone = Column(Enum('NORTE', 'SUR', 'ORIENTE', 'OCCIDENTE', name='zone'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('identification_number', 'email', name='uq_provider_identification_email'),
    )

class Role(db.Model):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)