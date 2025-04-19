import uuid, os, requests
from models.models import db, Seller, SellerJsonSchema
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

class GetSellers(Resource):
    def get(self):

        sellers = db.session.query(Seller).all()

        jsonSellers = SellerJsonSchema(
            many = True,
        ).dump(sellers)

        return {
            "sellers": jsonSellers
            
        }, 200
