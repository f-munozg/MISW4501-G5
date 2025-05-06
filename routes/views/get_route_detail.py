import uuid
from datetime import datetime
from flask_restful import Resource
from models.models import db, Route, RouteStop, RouteJsonSchema, StopsJsonSchema

class GetRouteDetail(Resource):
    def get(self, route_id):
                
        try:
            uuid.UUID(route_id)
        except:
            return {"message": "invalid route id"}, 400
        
        route = db.session.query(Route).filter(Route.id == route_id).first()

        if not route:
            return { "message": "route not found"}, 404

        stops = db.session.query(RouteStop).filter(route = route.id).all()

        json_route = RouteJsonSchema().dump(route)
        json_stops = StopsJsonSchema(
            many = True,
        ).dump(stops)
        
        return {
            "route": json_route,
            "stops": json_stops
        }, 200

