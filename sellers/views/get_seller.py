import uuid
from models.models import db, Seller, SellerJsonSchema
from flask_restful import Resource

class GetSeller(Resource):
    def get(self, seller_id):

        if not seller_id or seller_id == "":
            return {
                "message": "missing seller id"
            }, 400
        
        try:
            uuid.UUID(seller_id)
        except: 
            return {"message": "invalid seller id"}, 400

        seller = db.session.query(Seller).filter_by(id=seller_id).first()

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
