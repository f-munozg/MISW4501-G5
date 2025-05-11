import uuid
from datetime import datetime
from models.models import db, RouteStop, StopsJsonSchema
from flask_restful import Resource

class GetStops(Resource):
    def get(self):

        stops = db.session.query(RouteStop).filter(RouteStop.order_id != None).all()

        json_stops = StopsJsonSchema(
            many = True,
        ).dump(stops)

        return {
            "stops": json_stops
        }, 200