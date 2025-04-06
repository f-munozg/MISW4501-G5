from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, ForeignKey, Text, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum as SQLAlchemyEnum
import uuid
import enum

db = SQLAlchemy()

class ProductCategory(enum.Enum):
    FARMACIA = "Farmacia"
    ALIMENTACIÓN = "Alimentación"
    LIMPIEZA = "Limpieza"
    ELECTRÓNICA = "Electrónica"
    ROPA = "Ropa"
    HERRAMIENTAS = "Herramientas"
    BELLEZA = "Belleza"
    JUGUETE = "Juguete"
    HOGAR = "Hogar"

class Product(db.Model):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = Column(String(200), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    unit_value = Column(Float, nullable=False)
    conditions_storage = Column(String(200), nullable=False)
    product_features = Column(String(200), nullable=False)
    provider_id = Column(UUID(as_uuid=True), nullable=False)
    time_delivery_dear = Column(DateTime) 
    photo = Column(Text)
    description = Column(String(255))
    category = Column(SQLAlchemyEnum(ProductCategory), nullable=False)
