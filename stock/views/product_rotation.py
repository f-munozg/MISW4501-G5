import uuid
from flask import request
from sqlalchemy import or_
from flask_restful import Resource
from datetime import datetime, timedelta
from models.models import db, Product, HistoryStockLog, StockMovementType

class ProductRotationReport(Resource):
    def get(self):
        product_id = request.args.get("product_id")
        start_str = request.args.get("start_date")
        end_str = request.args.get("end_date")
        
        try:
            now = datetime.utcnow()
            start_date = datetime.fromisoformat(start_str) if start_str else now - timedelta(days=30)
            end_date = datetime.fromisoformat(end_str) if end_str else now
        except ValueError:
            return {"message": "Invalid date format. Use YYYY-MM-DD"}, 400
        
        try:
            product_uuid = uuid.UUID(product_id)
        except (ValueError, TypeError):
            return {"message": "Invalid or missing product_id"}, 400

        product = db.session.query(Product).filter_by(id=product_uuid).first()
        if not product:
            return {"message": "Product not found"}, 404

        stock_acumulado = 0
        stock_consumido = 0
        stock_inicial = 0
        stock_final = 0
        movimientos_detalle = []

        movimientos = db.session.query(HistoryStockLog).filter(
            HistoryStockLog.product_id == product_uuid,
            HistoryStockLog.timestamp.between(start_date, end_date),
            or_(
                HistoryStockLog.alert_message == "",
                HistoryStockLog.alert_message.is_(None)
            )
        ).order_by(HistoryStockLog.timestamp.asc()).all()

        for m in movimientos:
            if m.movement_type == StockMovementType.INGRESO:
                stock_inicial += m.quantity
            elif m.movement_type == StockMovementType.SALIDA:
                stock_final -= m.quantity

            cantidad_ingreso = m.quantity if m.movement_type.name == "INGRESO" else 0
            cantidad_salida = m.quantity if m.movement_type.name == "SALIDA" else 0

            if m.movement_type == StockMovementType.INGRESO:
                stock_acumulado += m.quantity
            elif m.movement_type == StockMovementType.SALIDA:
                stock_acumulado -= m.quantity

            movimientos_detalle.append({
                "timestamp": m.timestamp.strftime("%Y-%m-%d %H:%M"),
                "nombre_producto": product.name,
                "cantidad_ingreso": cantidad_ingreso,
                "cantidad_salida": cantidad_salida,
                "tipo_movimiento": str(m.movement_type.name),
                "stock_acumulado": stock_acumulado
            })

        stock_consumido = (stock_final*-1)
        stock_final = stock_inicial - stock_consumido

        if stock_inicial > 0:
            porcentaje_rotacion = round((stock_consumido / stock_inicial) * 100, 2)
        else:
            porcentaje_rotacion = 0.0

        if porcentaje_rotacion >= 80:
            nivel_rotacion = "Alta"
        elif porcentaje_rotacion >= 40:
            nivel_rotacion = "Media"
        else:
            nivel_rotacion = "Baja"

        return {
            "product_id": str(product.id),
            "sku": product.sku,
            "name": product.name,
            "rotacion": {
                "porcentaje": porcentaje_rotacion,
                "texto": f"{porcentaje_rotacion}%",
                "nivel": nivel_rotacion
            },
            "stock_inicial": stock_inicial,
            "stock_final": stock_final,
            "movimientos": movimientos_detalle
        }, 200