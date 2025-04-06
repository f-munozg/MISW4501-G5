from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Float
from sqlalchemy.dialects.postgresql import ARRAY, UUID
import uuid

db = SQLAlchemy()

class Seller(db.Model):
    __tablename__ = "sellers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    identification_number = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False, unique=True)
    email = Column(String(255), nullable=False)
    address = Column(String(255))
    phone = Column(String(255)) 
    zone = Column(Enum('NORTE', 'SUR', 'ORIENTE', 'OCCIDENTE', name='zone'), nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('identification_number', 'email', name='uq_provider_identification_email'),
    )