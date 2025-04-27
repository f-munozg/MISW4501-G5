import uuid, hashlib
from datetime import datetime
from models.models import db, Customer, Store, CustomerJsonSchema, StoreJsonSchema
from flask_restful import Resource

class GetCustomer(Resource):
    def get(self, user_id):

        if not user_id or user_id == "":
            return {
                "message": "missing user id"
            }, 400

        try:
            uuid.UUID(user_id)
        except: 
            return {"message": "invalid user id"}, 400

        customer = db.session.query(Customer).filter_by(user_id = user_id).first()
        if not customer:
            return {
                "message": "customer not found"
            }, 404
        
        store = db.session.query(Store).filter_by(customer_id = customer.id).first()
        if not store:
            return {
                "message": "store not found"
            }, 500

        jsonCustomer = CustomerJsonSchema().dump(customer)
        jsonStore = StoreJsonSchema().dump(store)

        return {
            "customer": jsonCustomer,
            "store": jsonStore
        }, 200
