from datetime import datetime
from flask_restful import Resource
from models.models import db, Truck, TruckJsonSchema

class GetTrucks(Resource):
    def get(self):
        trucks = db.session.query(Truck).all()

        json_trucks = TruckJsonSchema(
            many = True,
        ).dump(trucks)

        return {
            "trucks": json_trucks
        }, 200
