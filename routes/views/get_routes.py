import uuid
from datetime import datetime
from models.models import db, Route, RouteJsonSchema, RouteType, RouteStatus
from flask import request
from flask_restful import Resource

class GetRoutes(Resource):
    def get(self):
        type = request.args.get("type")
        assignee_id = request.args.get("assignee_id")
        status = request.args.get("status")

        query = []

        if type and type != "":
            if not type in RouteType:
                return {"message": "invalid route type"}, 400
            query.append(Route.type == RouteType(type))

        if status and status != "":
            if not status in RouteStatus:
                return {"message": "invalid route status"}, 400
            query.append(Route.status == RouteStatus(status))


        if assignee_id and assignee_id != "":
            try:
                uuid.UUID(assignee_id)
            except:
                return {"message": "invalid assignee id"}, 400
            
            query.append(Route.attendant == assignee_id)

        route = db.session.query(Route).filter(*query).all()

        json_route = RouteJsonSchema(many=True).dump(route)
        
        return {
            "routes": json_route
        
        }, 200
