import uuid
from datetime import datetime
from flask_restful import Resource
from models.models import db, Truck, TruckJsonSchema
from flask import request

class GetTrucks(Resource):
    def get(self):
        
        warehouse_id = request.args.get("warehouse_id")

        query = []

        if warehouse_id and warehouse_id != "":
            try:
                uuid.UUID(warehouse_id)
            except:
                return {"message": "invalid warehouse id"}, 400
            
            query.append(Truck.warehouse_id == warehouse_id)

        trucks = db.session.query(Truck).filter(*query).all()


        json_trucks = TruckJsonSchema(
            many = True,
        ).dump(trucks)

        return {
            "trucks": json_trucks
        }, 200
