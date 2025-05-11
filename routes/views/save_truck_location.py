import os, json, uuid
from flask import request
from datetime import datetime
from flask_restful import Resource
from models.models import db, Truck

class SaveTruckLocation(Resource):
    def post(self):
        data = request.get_json()
        # find truck
        required_fields = ["truck", "location"]

        
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return {
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, 400
        
        # Validar UUID
        try:
            truck_id = uuid.UUID(data.get("truck"))
        except ValueError:
            return {"message": "Invalid truck ID format"}, 400


        truck = db.session.query(Truck).filter(Truck.id == truck_id).first()

        if not truck:
            return {
                "message": "truck not found"
            }, 404
        
        # update data
        truck.location = data.get("location")
        db.session.commit()
        # return ok
        return {
            "message": "update successful"
        }, 200
