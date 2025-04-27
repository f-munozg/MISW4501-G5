# Nuevos endpoints: /stock/reserve y /stock/release
import uuid, os
from flask import request
from flask_restful import Resource
from models.models import db, Stock
from sqlalchemy.exc import SQLAlchemyError

class StockRelease(Resource):
    def post(self):
        data = request.json
        required_fields = ["product_id", "warehouse_id", "quantity", "user"]
        missing = [f for f in required_fields if f not in data or not data[f]]
        if missing:
            return {"message": f"Missing fields: {', '.join(missing)}"}, 400

        try:
            product_id = uuid.UUID(data["product_id"])
            warehouse_id = uuid.UUID(data["warehouse_id"])
            quantity = int(data["quantity"])
            if quantity <= 0:
                raise ValueError()
        except:
            return {"message": "Invalid product_id, warehouse_id or quantity"}, 400

        stock = db.session.query(Stock).filter_by(
            product_id=product_id,
            warehouse_id=warehouse_id
        ).first()

        if not stock or stock.reserved_quantity < quantity:
            return {"message": "Cannot release reservation: not enough reserved quantity"}, 409

        stock.reserved_quantity -= quantity

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": "Database error", "details": str(e)}, 500

        return {"message": "Reservation released successfully"}, 200
