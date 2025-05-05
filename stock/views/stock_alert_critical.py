import uuid
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from sqlalchemy import and_

from models.models import db, Stock, Product, Warehouse, HistoryStockLog, StockMovementType

class StockCriticalCheck(Resource):
    def post(self):
        try:
            critical_stocks = db.session.query(Stock).options(
                joinedload(Stock.product),
                joinedload(Stock.warehouse)
            ).filter(
                and_(
                    Stock.quantity <= Stock.threshold_stock,
                )
            ).all()

            if not critical_stocks:
                return {"message": "No critical stock found"}, 200

            response_data = []

            for stock in critical_stocks:
                stock.critical_level = True

                alert_msg = f"Producto {stock.product.name} en bodega {stock.warehouse.name} alcanzó nivel crítico."

                history = HistoryStockLog(
                    product_id=stock.product_id,
                    warehouse_id=stock.warehouse_id,
                    quantity=stock.quantity,
                    user="Sistema",
                    movement_type=StockMovementType.SALIDA,
                    alert_message=alert_msg
                )
                db.session.add(history)

                other_stock = db.session.query(Stock).filter(
                    Stock.product_id == stock.product_id,
                    Stock.warehouse_id != stock.warehouse_id,
                    Stock.quantity > Stock.threshold_stock
                ).all()

                if other_stock:
                    suggested_action = "Transferir stock desde otra bodega"
                else:
                    suggested_action = "Generar orden de compra al proveedor"

                # print(f"[NOTIFICACIÓN] {alert_msg} | Acción sugerida: {suggested_action}")

                response_data.append({
                    "product_id": str(stock.product_id),
                    "product_name": stock.product.name,
                    "warehouse": stock.warehouse.name,
                    "current_quantity": stock.quantity,
                    "threshold": stock.threshold_stock,
                    "alert_message": alert_msg,
                    "suggested_action": suggested_action
                })

            db.session.commit()

            return {"message": "Critical stock detected", "critical_products": response_data}, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": "Database error", "details": str(e)}, 500

        except Exception as e:
            return {"message": "Unexpected error", "details": str(e)}, 500
