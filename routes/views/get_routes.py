import uuid
from datetime import datetime
from models.models import db, Route, RouteStop, RouteJsonSchema, StopsJsonSchema
from flask import request
from flask_restful import Resource

class GetRoutes(Resource):
    def get(self):
        type = request.args.get("type")
        assignee_id = request.args.get("assignee_id")
        status = request.args.get("status")

        query = []

        if type and type != "":
            query.append(Route.type == type)

        if status and status != "":
            query.append(Route.status == status)


        if assignee_id and assignee_id != "":
            try:
                uuid.UUID(assignee_id)
            except:
                return {"message": "invalid assignee id"}, 400
            
            query.append(Route.attendant == assignee_id)

        route = db.session.query(Route).filter(*query).first()

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
