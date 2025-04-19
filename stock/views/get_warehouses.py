from datetime import datetime
from models.models import db, Warehouse, WarehouseJsonSchema
from flask_restful import Resource

class GetWarehouses(Resource):
    def get(self):

        warehouses = db.session.query(Warehouse).all()

        jsonWarehouses = WarehouseJsonSchema(
            many = True,
        ).dump(warehouses)

        return {
            "Warehouses": jsonWarehouses
        }, 200
