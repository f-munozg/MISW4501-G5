from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from sqlalchemy import Column, String, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum as SQLAlchemyEnum
import uuid, enum

db = SQLAlchemy()

class SellerZone(enum.Enum):
    NORTE = "NORTE"
    SUR = "SUR"
    ORIENTE = "ORIENTE"
    OCCIDENTE = "OCCIDENTE"

class AccessType(enum.Enum):
    ALLOW = 'allow'
    READONLY = 'readonly'
    DENY = 'deny'

class User(db.Model):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    email = Column(String(50), nullable=False)
    role = Column(UUID(as_uuid=True), ForeignKey('roles.id'), nullable=False)


class Role(db.Model):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)

class Privilege(db.Model):
    __tablename__ = "privileges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)
    module = Column(String(50), nullable=False)
    module_attribute = Column(String(50), nullable=False)
    access_type = Column(Enum(AccessType), nullable=False)

class Role_Privilege(db.Model):
    __tablename__ = "role_privilege"

    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id'), nullable=False)
    privilege_id = Column(UUID(as_uuid=True), ForeignKey('privileges.id'), nullable=False)

    __table_args__ = (
        db.PrimaryKeyConstraint('role_id', 'privilege_id'),
    )

class Seller(db.Model):
    __tablename__ = "sellers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    identification_number = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False, unique=True)
    email = Column(String(255), nullable=False)
    address = Column(String(255))
    phone = Column(String(255)) 
    zone = Column(SQLAlchemyEnum(SellerZone), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

class RoleJsonSchema(Schema):
    id = fields.UUID() 
    name = fields.Str()

class PrivilegeJsonSchema(Schema):
    name = fields.Str()
    module  = fields.Str()
    module_attribute  = fields.Str()
    access_type  = fields.Str()

class UsersJsonSchema(Schema):
    id = fields.UUID() 
    username = fields.Str()