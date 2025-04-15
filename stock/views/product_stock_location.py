from flask import request
from flask_restful import Resource
from models.models import db, Stock, Product
from datetime import date
from sqlalchemy import or_, and_

class ProductStockLocation(Resource):
    def get(self):
        search = request.args.get("product", default=None)
        warehouse_id = request.args.get("warehouse_id", default=None)
        
        if not search and not warehouse_id:
            return {"error": "Debe enviar al menos 'search' o 'warehouse_id'."}, 400

        try:
            limit = int(request.args.get("limit", 10))
            offset = int(request.args.get("offset", 0))
        except ValueError:
            return {"message": "limit and offset must be integers"}, 400
        
        filters = []

        if warehouse_id:
            filters.append(Stock.warehouse_id == warehouse_id)
        
        if search:
            filters.append(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.sku.ilike(f"%{search}%")
                )
            )

        base_query = db.session.query(
            Product.name.label("product_name"),
            Product.sku,
            Stock.quantity,
            Stock.location,
            Stock.expiration_date
        ).join(
            Stock, Stock.product_id == Product.id
        ).filter(
            and_(*filters)
        )

        total = base_query.count()
        results = base_query.offset(offset).limit(limit).all()

        data = []
        today = date.today()

        for row in results:
            status = "Vigente"
            if row.expiration_date and row.expiration_date.date() < today:
                status = "Vencido"

            data.append({
                "product": row.product_name,
                "sku": row.sku,
                "quantity": row.quantity,
                "location": row.location,
                "status": status
            })

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "results": data
        }, 200
