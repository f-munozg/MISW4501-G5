import uuid
from datetime import datetime
from models.models import db, RouteStop, StopsJsonSchema
from flask_restful import Resource

class GetStopsByCustomer(Resource):
    def get(self, customer_id):

        try:
            uuid.UUID(customer_id)
        except:
            return {"message": "invalid customer id"}, 400
        
        stops = db.session.query(RouteStop).filter(RouteStop.customer_id == customer_id).all()

        json_stops = StopsJsonSchema(
            many = True,
        ).dump(stops)

        return {
            "customer_id": customer_id,
            "stops": json_stops
        }