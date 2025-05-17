import uuid, random
from datetime import datetime
from models.models import db, RouteStop, StopsJsonSchema
from models.maps import RouteMaps
from flask_restful import Resource

class GetStopsByCustomer(Resource):
    def get(self, customer_id):

        try:
            uuid.UUID(customer_id)
        except:
            return {"message": "invalid customer id"}, 400
        
        stops = db.session.query(RouteStop).filter(RouteStop.customer_id == customer_id, RouteStop.order_id == None).all()

        json_stops = StopsJsonSchema(
            many = True,
        ).dump(stops)

        route = RouteMaps.routes[random.randint(0,len(RouteMaps.routes)-1)]

        return {
            "customer_id": customer_id,
            "stops": json_stops,
            "route_map": route
        }