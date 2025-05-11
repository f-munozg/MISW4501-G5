from datetime import datetime
from flask_restful import Resource
from models.models import db, Truck, TruckJsonSchema

class GetTrucksLocation(Resource):
    def get(self):
        trucks = db.session.query(Truck).all()

        json_trucks = TruckJsonSchema(
            many = True,
            only=  ("id", "location")
        ).dump(trucks)

        return {
            "trucks": json_trucks
        }, 200
