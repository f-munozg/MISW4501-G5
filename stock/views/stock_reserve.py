import uuid, os
from flask import request
from flask_restful import Resource
from models.models import db, Stock
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, and_

class StockReserve(Resource):
    def post(self):
        data = request.json
        required_fields = ["product_id", "quantity"]
        missing = [f for f in required_fields if f not in data or not data[f]]
        if missing:
            return {"message": f"Missing fields: {', '.join(missing)}"}, 400

        try:
            product_id = uuid.UUID(data["product_id"])
            quantityRequired = int(data["quantity"])
            if quantityRequired <= 0:
                raise ValueError()
        except:
            return {"message": "Invalid product_id or quantity"}, 400

        selected_stock = None
        selected_stock = db.session.query(Stock).filter(
            and_(
                Stock.product_id == product_id,
                (Stock.quantity - Stock.reserved_quantity) >= quantityRequired
            )
        ).first()

        if not selected_stock:
            return {
                "message": f"Insufficient available stock for reservation."
            }, 409

        selected_stock.reserved_quantity += quantityRequired

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": "Database error", "details": str(e)}, 500

        return {
            "message": "Reservation applied successfully",
            "warehouse_id": str(selected_stock.warehouse_id)
        }, 200
