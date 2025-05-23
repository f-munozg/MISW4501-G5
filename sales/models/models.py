from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, ForeignKey, Text, Float, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum as SQLAlchemyEnum
from marshmallow import Schema, fields
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

class PlanPeriod(enum.Enum):
    TRIMESTRAL = "Trimestral"
    SEMESTRAL = "Semestral"
    ANUAL = "Anual"

class StoreZone(enum.Enum):
    NORTE = "NORTE"
    SUR = "SUR"
    ORIENTE = "ORIENTE"
    OCCIDENTE = "OCCIDENTE"


class VisitStatus(enum.Enum):
    REALIZADA = "Realizada"
    NO_REALIZADA = "No Realizada"

class VisitResult(enum.Enum):
    PEDIDO = "Pedido"
    RESERVA = "Reserva"


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
    route_id = Column(UUID(as_uuid=True), nullable=True)
    order_total = Column(Float, nullable=False, default=0)
    status_payment = Column(String(50), nullable=False, default="")
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

class SalesPlan(db.Model):
    __tablename__ = "sales_plan"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id = Column(UUID(as_uuid=True))
    target = Column(String(50), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False)
    period = Column(SQLAlchemyEnum(PlanPeriod), nullable=False)
    active = Column(Boolean, default=True, nullable=False)


class Visit(db.Model):
    __tablename__ = "visit"

    id = db.Column(db.Integer, primary_key=True)
    seller_id = Column(UUID(as_uuid=True), nullable=False)
    customer_id = Column(UUID(as_uuid=True), nullable=False)
    store_address = Column(String(50), nullable=False)
    zone = Column(SQLAlchemyEnum(StoreZone), nullable=False)
    visit_status = Column(SQLAlchemyEnum(VisitStatus), nullable=False)
    visit_result = Column(SQLAlchemyEnum(VisitResult), nullable=True)
    observations = Column(String(200), nullable=False)
    


class SalesJsonSchema(Schema):
    id = fields.UUID()
    name = fields.Str()
    total_quantity = fields.Float()
    unit_value = fields.Float()
    purchase_date = fields.Str()