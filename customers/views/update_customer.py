import uuid, hashlib, requests, os
from datetime import datetime
from models.models import db, Customer, Store, User, CustomerJsonSchema, StoreJsonSchema
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

class UpdateCustomer(Resource):
    def put(self, user_id):
        data = request.json

        required_fields = [
            "name", "email", "identification_number", "store_id_number", "store_address", "store_phone"
        ]

        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return {
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, 400
        
        try:
            uuid.UUID(user_id)
        except: 
            return {"message": "Invalid user ID"}, 400
        
        user = db.session.query(User).filter_by(id=user_id).first()

        if not user:
            return {
                "message": "invalid user id"
            }, 404
        
        customer = db.session.query(Customer).filter_by(user_id=user.id).first()

        if not customer: 
            return {
                "message": "customer not found"
            }, 500
        
        store = db.session.query(Store).filter_by(customer_id=customer.id).first()

        if not store: 
            return {
                "message": "store not found"
            }, 500
        
        customer.name = data.get("name")
        customer.identification_number = data.get('identification_number')
        
        store.identification_number = data.get('store_id_number')
        store.address = data.get('store_address')
        store.phone = data.get('store_phone')

        db.session.commit()

        jsonCustomer = CustomerJsonSchema().dump(customer)
        jsonStore = StoreJsonSchema().dump(store)

        return {
            "message": "customer updated successfully",
            "store": jsonStore,
            "customer": jsonCustomer
        }, 202