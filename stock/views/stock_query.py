from flask import request
from flask_restful import Resource
from models.models import db, Stock, Product, Warehouse, ProductCategory
from sqlalchemy import and_

class StockyQuery(Resource):
    def get(self):
        product_name = request.args.get("product")
        provider_id = request.args.get("provider")
        category_name = request.args.get("category")

        try:
            limit = int(request.args.get("limit", 10))
            offset = int(request.args.get("offset", 0))
        except ValueError:
            return {"message": "limit and offset must be integers"}, 400

        if category_name:
            try:
                category_enum = ProductCategory[category_name.upper()]
            except KeyError:
                valid = [cat.name for cat in ProductCategory]
                return {
                    "message": f"Invalid category '{category_name}'. Valid options are: {', '.join(valid)}"
                }, 400
        else:
            category_enum = None

        base_query = db.session.query(
            Warehouse.name.label("warehouse_name"),
            Product.name.label("product_name"),
            Product.category.label("category"),
            Product.estimated_delivery_time.label("estimated_delivery_time"),
            Stock.date_update.label("date_update"),
            Stock.quantity
        ).join(Stock, Stock.warehouse_id == Warehouse.id
        ).join(Product, Product.id == Stock.product_id)

        filters = []
        if product_name:
            filters.append(Product.name.ilike(f"%{product_name}%"))
        if provider_id:
            filters.append(Product.provider_id == provider_id)
        if category_enum:
            filters.append(Product.category == category_enum)

        if filters:
            base_query = base_query.filter(and_(*filters))

        total = base_query.count()
        results = base_query.offset(offset).limit(limit).all()

        data = [
            {
                "warehouse": row.warehouse_name,
                "product": row.product_name,
                "category": row.category.value,
                "quantity": row.quantity,
                "estimated_delivery_time": row.estimated_delivery_time.isoformat() if row.estimated_delivery_time else None,
                "date_update": row.date_update.isoformat() if row.date_update else None
            }
            for row in results
        ]

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "results": data
        }, 200
