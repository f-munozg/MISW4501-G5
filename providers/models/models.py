from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Float
from sqlalchemy.dialects.postgresql import ARRAY, UUID
import uuid

db = SQLAlchemy()

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
    type_rule = Column(Enum('LEGAL', 'COMERCIAL', 'TRIBUTARIA', name='type_rule'), nullable=False)
    value_rule = Column(Float, nullable=False)
    description = Column(String(250), nullable=False)
    regulatory_entity = Column(String(200), nullable=False)

class Portfolio_Rule(db.Model):
    __tablename__ = "portfolio_rules"

    portfolio_id = Column(UUID(as_uuid=True), ForeignKey('portfolio.id'), nullable=False)
    rule_id = Column(UUID(as_uuid=True), ForeignKey('rules.id'), nullable=False)

    __table_args__ = (
        db.PrimaryKeyConstraint('portfolio_id', 'rule_id'),
    )
