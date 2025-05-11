import uuid
from flask import request
from flask_restful import Resource
from sqlalchemy import and_
from models.models import db, Order

class GetSellersWithOrders(Resource):
    def get(self):
        fecha_inicio = request.args.get("fecha_inicio")
        fecha_fin = request.args.get("fecha_fin")
        vendedor = request.args.get("vendedor")  # opcional

        if not fecha_inicio or not fecha_fin:
            return {"message": "Se requieren fecha_inicio y fecha_fin"}, 400

        query = db.session.query(Order).filter(
            and_(
                Order.date_order >= fecha_inicio,
                Order.date_order <= fecha_fin,
                Order.status.in_(["created", "paid"])
            )
        )

        if vendedor:
            try:
                uuid.UUID(vendedor)
            except:
                return {"message": "vendedor no es un UUID válido"}, 400
            query = query.filter(Order.seller_id == vendedor)

        ordenes = query.all()

        if not ordenes:
            return {"message": "No se encontraron órdenes válidas en el rango dado"}, 404

        seller_ids = list({str(o.seller_id) for o in ordenes if o.seller_id})

        return {
            "seller_ids": seller_ids
        }, 200
