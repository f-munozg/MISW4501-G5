from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum as SQLAlchemyEnum
import uuid
import enum
from datetime import datetime

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
    storage_conditions = Column(String(200), nullable=False)
    product_features = Column(String(200), nullable=False)
    provider_id = Column(UUID(as_uuid=True), nullable=False)
    estimated_delivery_time = Column(DateTime) 
    photo = Column(Text)
    description = Column(String(255))
    category = Column(SQLAlchemyEnum(ProductCategory), nullable=False)

    stock = db.relationship("Stock", back_populates="product")


class Stock(db.Model):
    __tablename__ = "stock"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouse.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    threshold_stock = Column(Integer, nullable=False)
    critical_level = Column(Boolean, nullable=False)
    date_update = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    location = Column(String(200), nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)


    product = db.relationship("Product", back_populates="stock")
    warehouse = db.relationship("Warehouse", back_populates="stock")


class Warehouse(db.Model):
    __tablename__ = "warehouse"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    address = Column(String(200), nullable=False)
    country = Column(String(200), nullable=False)
    city = Column(String(200), nullable=False)
    location = Column(String(200), nullable=True)
    storage_volume = Column(Integer, nullable=False)
    available_volume = Column(Integer, nullable=False)
    truck_capacity = Column(Integer, nullable=False)

    stock = db.relationship("Stock", back_populates="warehouse")
