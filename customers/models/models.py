from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, ForeignKey, Text, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum as SQLAlchemyEnum
from marshmallow import Schema, fields
import uuid
import enum


db = SQLAlchemy()

class MeansOfPayment(enum.Enum):
    TRANSFERENCIA_BANCARIA = "Transferencia bancaria"
    PAGO_ENTRE_CELULARES = "Pago entre celulares"

class TypeOfPayment(enum.Enum):
    PARCIAL = "Parcial"
    COMPLETO = "Completo"

class User(db.Model):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    email = Column(String(50), nullable=False)
    role = Column(UUID(as_uuid=True), ForeignKey('roles.id'), nullable=False)


class Customer(db.Model):
    __tablename__ = "customers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=True)
    identification_number = Column(String(50), unique=True, nullable=True)
    assigned_seller = Column(UUID(as_uuid=True))
    observations = Column(String(200), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

class Store(db.Model):
    __tablename__ = "store"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    identification_number = Column(String(50), unique=True, nullable=True)
    address = Column(String(50), nullable=True)
    city = Column(String(50), nullable=True)
    country = Column(String(50), nullable=True)
    phone = Column(String(50), nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)

class Role(db.Model):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)

class Payment(db.Model):
    __tablename__ = "payment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), nullable = False)
    date_payment = Column(DateTime)
    type_payment = Column(SQLAlchemyEnum(TypeOfPayment), nullable=False)
    mean_payment = Column(SQLAlchemyEnum(MeansOfPayment), nullable=False)
    voucher_payment = Column(Text)

class CustomerJsonSchema(Schema):
    id = fields.UUID()
    name = fields.Str()
    identification_number  = fields.Str()
    assigned_seller  = fields.UUID()
    observations  = fields.Str()
    user_id = fields.UUID()
    email = fields.Str()

class StoreJsonSchema(Schema):
    id = fields.UUID()
    identification_number = fields.Str()
    address = fields.Str()
    city = fields.Str()
    country = fields.Str()
    phone = fields.Str()