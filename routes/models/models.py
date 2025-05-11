from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String,  Boolean, Float, DateTime
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from marshmallow import Schema, fields
from sqlalchemy import Enum as SQLAlchemyEnum
import uuid, enum

db = SQLAlchemy()

class RouteType(enum.Enum):
    ENTREGA = "Entrega"
    VISITA = "Visita"

class RouteStatus(enum.Enum):
    CREADA = "Creada"
    CONFIRMADA = "Confirmada"
    EN_RUTA = "En Ruta"
    RETRASADA = "Retrasada"
    COMPLETADA = "Completada"

class StopStatus(enum.Enum):
    PENDIENTE = "Pendiente"
    COMPLETADA = "Completada"
    FALLIDA = "Fallida"

class StopResult(enum.Enum):
    RECIBIDO = "Recibido" # Parada Entrega
    RECHAZADO = "Rechazado" # Parada Entrega
    RESERVA = "Reserva" # Parada Visita
    PEDIDO = "Pedido" # Parada Visita
    

class RouteStop(db.Model):
    __tablename__ = 'route_stop'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    eta = Column(Float)
    order_id = Column(UUID(as_uuid=True), nullable=True)
    customer_id = Column(UUID(as_uuid=True), nullable=False)
    route_id = Column(UUID(as_uuid=True), nullable=False)
    observations = Column(String(255))
    status = Column(SQLAlchemyEnum(StopStatus), nullable=False)
    result = Column(SQLAlchemyEnum(StopResult), nullable=True)
    optional = Column(Boolean, nullable=False)

    

class Truck(db.Model):
    __tablename__ = 'trucks'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    warehouse_id = Column(UUID(as_uuid=True))
    capacity = Column(Float, nullable=False)
    location = Column(String(25))
    available = Column(Boolean)
    updated_at = Column(DateTime)

class Route(db.Model):
    __tablename__  =  'routes'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(SQLAlchemyEnum(RouteType), nullable=False)
    attendant = Column(UUID(as_uuid=True), nullable=False) # seller or truck
    status = Column(SQLAlchemyEnum(RouteStatus), nullable=False)
    date_route = Column(DateTime)
    updated_at = Column(DateTime)

class RouteJsonSchema(Schema):
    id = fields.UUID()
    type = fields.Enum(RouteType)
    attendant = fields.UUID()
    status = fields.Enum(RouteStatus)
    date_route = fields.DateTime()
    
class StopsJsonSchema(Schema):
    id = fields.UUID()
    eta = fields.Float()
    store = fields.UUID()
    order_id = fields.UUID()
    customer_id = fields.UUID()
    observations = fields.Str()
    status = fields.Enum(StopStatus)
    result = fields.Enum(StopResult)
    optional = fields.Boolean()

class TruckJsonSchema(Schema):
    id = fields.UUID()
    user_id = fields.UUID()
    capacity = fields.Float()
    location = fields.Str()
    available = fields.Boolean()
    updated_at = fields.DateTime()