from flask import request
from flask_restful import Resource
from models.models import db, Event

class LogEvent(Resource):
    def post(self):
        data = request.json

        name = data.get("name")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        location = data.get("location")

        required_fields = [
            "name", "start_date", "end_date", "location"]

        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return {
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, 400
        
        event = Event(
            name = name,
            start_date = start_date,
            end_date = end_date,
            location = location
        )

        db.session.add(event)
        db.session.commit()

        return {
            "message": "event added successfully"
        }, 201
        