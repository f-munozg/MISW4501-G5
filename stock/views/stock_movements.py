import uuid
import time
from flask import request
from flask_restful import Resource
from models.models import db, Stock, HistoryStockLog, Product, Warehouse
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

class StockMovement(Resource):
    def post(self):
        start_time = time.time()
        data = request.json

        required_fields = ["product_id", "warehouse_id", "quantity", "user", "movement_type"]
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        if missing_fields:
            return {"message": f"Missing required fields: {', '.join(missing_fields)}"}, 400

        try:
            product_id = uuid.UUID(data["product_id"])
            warehouse_id = uuid.UUID(data["warehouse_id"])
        except ValueError:
            return {"message": "Invalid UUID format for product_id or warehouse_id"}, 400

        movement_type = data["movement_type"].upper()
        if movement_type not in {"INGRESO", "SALIDA"}:
            return {"message": "Invalid movement_type. Must be 'INGRESO' or 'SALIDA'"}, 400

        try:
            quantity = int(data["quantity"])
            if quantity <= 0:
                raise ValueError()
        except ValueError:
            return {"message": "Quantity must be a positive integer"}, 400

        stock_record = db.session.query(Stock).filter_by(
            product_id=product_id,
            warehouse_id=warehouse_id
        ).first()

        alert = None

        if stock_record:
            if movement_type == "SALIDA":
                if stock_record.quantity < quantity:
                    alert = "Insufficient stock for requested quantity"
                    db.session.add(HistoryStockLog(
                        product_id=product_id,
                        warehouse_id=warehouse_id,
                        quantity=quantity,
                        user=data["user"],
                        movement_type=movement_type,
                        timestamp=datetime.utcnow(),
                        alert_message=alert
                    ))
                    db.session.commit()
                    return {"message": alert}, 409
                stock_record.quantity -= quantity
                if stock_record.quantity < stock_record.threshold_stock:
                    stock_record.critical_level = True
            else:
                stock_record.quantity += quantity
                if stock_record.quantity >= stock_record.threshold_stock:
                    stock_record.critical_level = False
        else:
            if movement_type == "SALIDA":
                return {"message": "No stock record found. Cannot perform SALIDA."}, 404

            extra_required = ["threshold_stock", "critical_level", "location", "expiration_date"]
            missing_extra = [f for f in extra_required if f not in data or data[f] is None]
            if missing_extra:
                return {
                    "message": f"Missing fields to create new stock: {', '.join(missing_extra)}"
                }, 400

            try:
                new_stock = Stock(
                    product_id=product_id,
                    warehouse_id=warehouse_id,
                    quantity=quantity,
                    threshold_stock=int(data["threshold_stock"]),
                    critical_level=bool(data["critical_level"]),
                    location=data["location"],
                    expiration_date=datetime.fromisoformat(data["expiration_date"])
                )
            except Exception as e:
                return {"message": "Invalid data for stock creation", "details": str(e)}, 400

            db.session.add(new_stock)

        log = HistoryStockLog(
            product_id=product_id,
            warehouse_id=warehouse_id,
            quantity=quantity,
            user=data["user"],
            movement_type=movement_type,
            timestamp=datetime.utcnow(),
            alert_message=alert
        )

        try:
            db.session.add(log)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return {
                "message": "Error processing inventory movement",
                "details": str(e)
            }, 500

        elapsed = round(time.time() - start_time, 3)
        return {
            "message": "Stock movement processed successfully",
            "movement_type": movement_type,
            "time_elapsed_seconds": elapsed
        }, 201
