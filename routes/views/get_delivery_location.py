import uuid
from datetime import datetime
from flask_restful import Resource
from models.models import db, Route, Truck, TruckJsonSchema

class GetDeliveryLocation(Resource):
    def get(self, route_id):
        
        try:
            uuid.UUID(route_id)
        except:
            return {"message": "invalid route id"}, 400
        
        route = db.session.query(Route).filter(Route.id == route_id, Route.type == "Entrega", Route.status != "Completada").first()

        if not route:
            return {"message": "active route not found"}, 404
        
        truck = db.session.query(Truck).filter_by(id = route.attendant).first()

        if not truck:
            return {"message": "error getting truck info"}, 500
        
        json_truck = TruckJsonSchema(
            only=  ("id", "location")
        )

        return {
            "truck": json_truck
        }, 200
