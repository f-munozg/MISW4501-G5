import uuid, random
from flask_restful import Resource
from models.models import db, Product, Stock
from models.suggestions import Suggestions

class PurchaseSuggestions(Resource):
    def get(self, user_id):
        if not user_id or user_id == "":
            return {
                "message": "missing user id"
            }, 400

        try:
            uuid.UUID(user_id)
        except: 
            return {"message": "invalid user id"}, 400
        
        
        products = db.session.query(
            Product.id,
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
        ).limit(
            10
        ).all()

        data = [
            {
                "id": str(row.id),
                "product": row.product_name,
                "sku": row.sku,
                "photo": row.photo,
                "category": row.category.value if row.category else None,
                "quantity": row.quantity,
                "estimated_delivery_time": row.estimated_delivery_time.isoformat() if row.estimated_delivery_time else None,
                "date_update": row.date_update.isoformat() if row.date_update else None,
                "unit_value": row.unit_value
            }
            for row in products
        ]

        return {
            "products": data,
            "placement": Suggestions.placement[random.randint(0, len(Suggestions.placement)-1)],
            "purchase": Suggestions.suggestions[random.randint(0, len(Suggestions.suggestions)-1)],
        }, 200