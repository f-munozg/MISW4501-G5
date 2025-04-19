from models.models import db, Customer
from flask import request
from flask_restful import Resource

class AssignSeller(Resource):
    def post(self):
        data = request.json

        required_fields = [
            "customers", "seller_id" 
        ]

        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return {
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, 400
        
        for customer in data.get('customers'):
            customer = db.session.query(Customer).filter_by(id = customer).first()
            customer.assigned_seller = data.get('seller_id')
            db.session.commit()

        return {
            "message": "seller assigned successfully"
        }, 200