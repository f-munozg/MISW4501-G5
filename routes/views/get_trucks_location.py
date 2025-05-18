import random
from datetime import datetime
from flask_restful import Resource
from models.models import db, Truck, TruckJsonSchema
from models.maps import RouteMaps

class GetTrucksLocation(Resource):
    def get(self):
        trucks = db.session.query(Truck).all()

        json_trucks = TruckJsonSchema(
            many = True,
            only=  ("id", "location")
        ).dump(trucks)

        map = RouteMaps.trucklocations[random.randint(0,len(RouteMaps.trucklocations)-1)]

        return {
            "trucks": json_trucks,
            "map": map
        }, 200
