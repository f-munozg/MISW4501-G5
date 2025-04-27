import uuid
from flask import request
from models.models import db, Seller, SellerJsonSchema
from flask_restful import Resource

class GetSeller(Resource):
    def get(self):

        seller_id = request.args.get('seller_id')
        user_id = request.args.get('user_id')

        if (not seller_id or seller_id == "") and (not user_id or user_id == ""):
            return {
                "message": "missing id"
            }, 400
        
        if seller_id and seller_id != "":
            try:
                uuid.UUID(seller_id)
            except: 
                return {"message": "invalid seller id"}, 400
        
        if user_id and user_id != "":
            try:
                uuid.UUID(user_id)
            except: 
                return {"message": "invalid user id"}, 400
            
        query = []
        if seller_id and seller_id != "":
            query.append(Seller.id == seller_id)
        if user_id and user_id != "":
            query.append(user_id == user_id)
        
        seller = db.session.query(Seller).filter(*query).first()


        if not seller:
            return {
                "message": "seller not found"
            }, 404


        jsonSeller = SellerJsonSchema(
            only=  ( "id", "identification_number", "name", "email", "address", "phone", "zone", "user_id")
        ).dump(seller)

        return {
         "seller": jsonSeller
        }, 200
