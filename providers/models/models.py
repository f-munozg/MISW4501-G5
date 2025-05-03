from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from sqlalchemy import Column, String, Integer, ForeignKey, Float
from sqlalchemy.dialects.postgresql import ARRAY, UUID
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

class TypeRule(enum.Enum):
    LEGAL = "Legal"
    COMERCIAL = "Comercial"
    TRIBUTARIA = "Tributaria"

class TipoImpuesto(enum.Enum):
    RENTA_PERSONAS_FISICAS = "Renta Personas Físicas"
    SOCIEDADES = "Sociedades"
    PATRIMONIO = "Patrimonio"
    VALOR_AGREGADO = "Valor Agregado"
    ESPECIAL = "Especial"
    AMBIENTAL = "Ambiental"
    TRANSACCIONES_FINANCIERAS = "Transacciones Financieras"
    SUCESIONES_DONACIONES = "Sucesiones y Donaciones"
    BIENES_INMUEBLES = "Bienes Inmuebles"
    OTRO = "Otro"

class TipoReglaComercial(enum.Enum):
    Descuento = "Descuento"
    Pedido_Minimo = "Pedido Mínimo"
    Otro = "Otro"

class Provider(db.Model):
    __tablename__ = "providers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    identification_number = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    address = Column(String(255))
    countries = Column(ARRAY(String), nullable=False)
    identification_number_contact = Column(String(50), nullable=False)
    name_contact = Column(String(200), nullable=False)
    phone_contact = Column(String(255)) 
    address_contact = Column(String(255))

    portfolios = db.relationship('Portfolio', back_populates='provider', cascade="all, delete-orphan")

class Portfolio(db.Model):
    __tablename__ = "portfolio"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    product_id = Column(Integer, nullable=False)
    provider_id = Column(UUID(as_uuid=True), ForeignKey('providers.id'), nullable=False)

    provider = db.relationship('Provider', back_populates='portfolios')

class Rule(db.Model):
    __tablename__ = "rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    country = Column(String(100), nullable=False)
    type_rule = Column(SQLAlchemyEnum(TypeRule), nullable=False)
    # Campos comunes
    description = Column(String(500), nullable=True)
    
    # Campos específicos para reglas tributarias
    type_tax = Column(SQLAlchemyEnum(TipoImpuesto), nullable=True)
    value_tax = Column(Float, nullable=True)  # Porcentaje o monto fijo

    # Campos específicos para reglas comerciales
    tipo_regla_comercial = Column(SQLAlchemyEnum(TipoReglaComercial), nullable=True)

    # Campos específicos para reglas legales
    categoria_producto = Column(String(100), nullable=True)

class Portfolio_Rule(db.Model):
    __tablename__ = "portfolio_rules"

    portfolio_id = Column(UUID(as_uuid=True), ForeignKey('portfolio.id'), nullable=False)
    rule_id = Column(UUID(as_uuid=True), ForeignKey('rules.id'), nullable=False)

    __table_args__ = (
        db.PrimaryKeyConstraint('portfolio_id', 'rule_id'),
    )

class ProviderJsonSchema(Schema):
    id = fields.UUID()
    identification_number = fields.Str()
    name = fields.Str()
    address = fields.Str()
    countries = fields.List(fields.Str())
    identification_number_contact = fields.Str()
    name_contact = fields.Str()
    phone_contact = fields.Str()
    address_contact = fields.Str()
