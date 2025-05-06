import uuid
from datetime import datetime
from flask_restful import Resource
from models.models import db, Route

class ConfirmRoute(Resource):
    def put(self, route_id):

        try:
            uuid.UUID(route_id)
        except:
            return {"message": "invalid route id"}, 400
        
        route = db.session.query(Route).filter(Route.id == route_id).first()

        if not route:
            return { "message": "route not found"}, 404
        
        route.status = "Confirmada"

        db.commit()

        
        return {
            "message": "route confirmed successfully"
        }, 200
