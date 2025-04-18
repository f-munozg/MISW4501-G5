import uuid, hashlib
from datetime import datetime
from models.models import db, Customer, CustomerJsonSchema
from flask_restful import Resource

class GetAvailableCustomers(Resource):
    def get(self):

        customers = db.session.query(Customer).filter_by(assigned_seller = None).all()

        jsonCustomers = CustomerJsonSchema(
            many = True,
        ).dump(customers)

        return {
            "customers": jsonCustomers
        }, 200
