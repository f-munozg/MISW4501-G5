from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, ForeignKey, Text, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum as SQLAlchemyEnum
from marshmallow import Schema, fields
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

class Order(db.Model):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), nullable=False)
    seller_id = Column(UUID(as_uuid=True))
    date_order = Column(DateTime)
    date_delivery = Column(DateTime)
    status = Column(String(50), nullable=False)
    order_total = Column(Float, nullable=False, default=0)
    status_payment = Column(String(50), nullable=False, default="pending")
    products = db.relationship("OrderProducts", backref="order", lazy="joined", cascade="all, delete-orphan")

class OrderProducts(db.Model):
    __tablename__ = "order_products"

    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False)
    quantity = Column(Float, nullable=False)
    warehouse_id = Column(UUID(as_uuid=True), nullable=False)

    __table_args__ = (
        db.PrimaryKeyConstraint('order_id', 'product_id'),
    )

class Payments(db.Model):
    __tablename__ = "payments"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = db.Column(UUID(as_uuid=True), db.ForeignKey('orders.id'), nullable=False)
    total = db.Column(Float, nullable=False)
    payment = db.Column(Float, nullable=False)
    balance = db.Column(Float, nullable=False)
    payment_date = db.Column(DateTime, nullable=False, default=datetime.utcnow)
        
    order = db.relationship("Order", backref="payments")

class OrderJsonSchema(Schema):
    id = fields.UUID()
    customer_id = fields.UUID()
    seller_id = fields.UUID()
    date_order = fields.DateTime()
    date_delivery = fields.DateTime()
    status = fields.Str()
    order_total = fields.Float()
    status_payment = fields.Str()

class PaymentSummarySchema(Schema):
    total_amount = fields.Float()
    paid_amount = fields.Float()
    pending_balance = fields.Float()
    last_payment_date = fields.DateTime(allow_none=True)