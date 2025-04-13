import uuid, hashlib
from datetime import datetime
from models.models import db, Product, ProductJsonSchema
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

class GetProviderProducts(Resource):
    def get(self, provider_id):

        if not provider_id or provider_id == "":
            return {
                "message": "missing provider id"
            }, 400

        try:
            uuid.UUID(provider_id)
        except: 
            return {"message": "invalid provider id"}, 400

        products = db.session.query(Product).filter_by(provider_id = provider_id).all()

        jsonProducts = ProductJsonSchema(
            many = True,
        ).dump(products)

        return {
            "provider_id": provider_id,
            "products": jsonProducts
        }, 200
