import uuid, hashlib
from datetime import datetime
from models.models import db, Customer, CustomerJsonSchema
from flask_restful import Resource

class GetCustomers(Resource):
    def get(self):

        customers = db.session.query(Customer).all()

        jsonCustomers = CustomerJsonSchema(
            many = True,
        ).dump(customers)

        return {
            "customers": jsonCustomers
        }, 200
