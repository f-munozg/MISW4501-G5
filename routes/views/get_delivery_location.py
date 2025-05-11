import uuid
from datetime import datetime
from flask_restful import Resource
from models.models import db, Route, Truck, TruckJsonSchema, RouteStatus, RouteType, RouteStop

class GetDeliveryLocation(Resource):
    def get(self, order_id):
        
        try:
            uuid.UUID(order_id)
        except:
            return {"message": "invalid order id"}, 400
        
        route = db.session.query(Route).join(RouteStop, Route.id == RouteStop.route_id).filter(
            RouteStop.order_id == order_id, Route.status != RouteStatus.COMPLETADA).first()

        if not route:
            return {"message": "active route not found"}, 404
        
        truck = db.session.query(Truck).filter_by(id = route.attendant).first()

        if not truck:
            return {"message": "error getting truck info"}, 500
        
        json_truck = TruckJsonSchema(
            only=  ("id", "location")
        ).dump(truck)

        return {
            "truck": json_truck
        }, 200
