import uuid
from datetime import datetime
from flask_restful import Resource
from models.models import db, Route, RouteStop

class ConfirmRoute(Resource):
    def put(self, route_id):

        try:
            uuid.UUID(route_id)
        except:
            return {"message": "invalid route id"}, 400
        
        route = db.session.query(Route).filter(Route.id == route_id).first()

        if not route:
            return { "message": "route not found"}, 404
        
        stops = db.session.query(RouteStop).filter(RouteStop.id == route.id).all()

        if len(stops) <= 0:
            route.status = "Completada"
            db.commit()
            return {"message": "empty route"}, 204

        route.status = "Confirmada"
        db.commit()
        
        return {
            "message": "route confirmed successfully"
        }, 200
