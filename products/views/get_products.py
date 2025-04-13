import uuid, hashlib
from datetime import datetime
from models.models import db, Product, ProductJsonSchema
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

class GetProducts(Resource):
    def get(self):

        products = db.session.query(Product).all()

        jsonProducts = ProductJsonSchema(
            many = True,
        ).dump(products)

        return {
            "products": jsonProducts
        }, 200
