import uuid
from models.models import db, Order, OrderProducts
from flask import request
from flask_restful import Resource
from sqlalchemy import or_

class GetOrdersFinished(Resource):
    def get(self):
        fecha_inicio = request.args.get("fecha_inicio")
        fecha_fin = request.args.get("fecha_fin")

        query = db.session.query(Order).filter(
            or_(
                Order.status.ilike("created"),
                Order.status.ilike("paid")
            )
        )

        if fecha_inicio:
            query = query.filter(Order.date_order >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Order.date_order <= fecha_fin)

        ordenes = query.all()

        if not ordenes:
            return {"message": "No orders found"}, 404

        resultado = []
        for orden in ordenes:
            detalles = db.session.query(OrderProducts).filter_by(order_id=orden.id).all()
            detalle_list = [
                {
                    "product_id": str(d.product_id),
                    "quantity": d.quantity
                } for d in detalles
            ]

            resultado.append({
                "id": str(orden.id),
                "customer_id": str(orden.customer_id),
                "seller_id": str(orden.seller_id),
                "date_order": orden.date_order.isoformat(),
                "date_delivery": orden.date_delivery.isoformat() if orden.date_delivery else None,
                "status": orden.status,
                "detalle": detalle_list
            })

        return {"orders": resultado}, 200