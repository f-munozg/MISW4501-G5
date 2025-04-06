from flask import request
from flask_restful import Resource
from models.models import db, Product, Stock
from sqlalchemy import and_

class ProductWithStock(Resource):
    def get(self):
        try:
            limit = int(request.args.get("limit", 10))
            offset = int(request.args.get("offset", 0))
        except ValueError:
            return {"message": "limit and offset must be integers"}, 400

        base_query = db.session.query(
            Product.name.label("product_name"),
            Product.sku,
            Product.photo,
            Product.category.label("category"),
            Product.estimated_delivery_time,
            Stock.quantity,
            Stock.date_update,
            Product.unit_value
        ).join(
            Stock, Stock.product_id == Product.id
        ).filter(
            Stock.quantity > 0
        )

        total = base_query.count()
        results = base_query.offset(offset).limit(limit).all()

        data = [
            {
                "product": row.product_name,
                "sku": row.sku,
                "photo": row.photo,
                "category": row.category.value if row.category else None,
                "quantity": row.quantity,
                "estimated_delivery_time": row.estimated_delivery_time.isoformat() if row.estimated_delivery_time else None,
                "date_update": row.date_update.isoformat() if row.date_update else None,
                "unit_value": row.unit_value
            }
            for row in results
        ]

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "results": data
        }, 200
