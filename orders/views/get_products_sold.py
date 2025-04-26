import uuid
from models.models import db, Order, Product, OrderProducts
from flask import request
from flask_restful import Resource
from sqlalchemy import and_
from sqlalchemy.orm import joinedload

class GetProductsSold(Resource):
    def get(self):
        product_id = request.args.get("product_id")
        fecha_inicio = request.args.get("fecha_inicio")
        fecha_fin = request.args.get("fecha_fin")

        if fecha_inicio is None or fecha_fin is None:
            return {"message": "fecha_inicio y fecha_fin son requeridos"}, 400

        try:
            if product_id:
                uuid.UUID(product_id)
        except:
            return {"message": "product_id inválido"}, 400

        query = db.session.query(Product).join(OrderProducts).join(Order).filter(
            and_(
                Order.date_order >= fecha_inicio,
                Order.date_order <= fecha_fin
            )
        )

        if product_id:
            query = query.filter(Product.id == product_id)

        query = query.distinct()

        productos = query.all()

        if not productos:
            return {"message": "No se encontraron productos vendidos en el rango dado"}, 404

        resultado = [
            {
                "id": str(p.id),
                "name": p.name,
                "sku": p.sku,
                "unit_value": p.unit_value
            }
            for p in productos
        ]

        return {"productos": resultado}, 200
