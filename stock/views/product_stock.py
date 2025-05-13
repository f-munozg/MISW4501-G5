import uuid
from models.models import db, Stock, StockJsonSchema
from flask_restful import Resource

class GetProductStock(Resource):
    def get(self, product_id):
        if not product_id or product_id == "":
            return {
                "message": "missing product id"
            }, 400

        try:
            uuid.UUID(product_id)
        except: 
            return {"message": "invalid product id"}, 400

        stock = db.session.query(Stock).filter(Stock.product_id == product_id, Stock.quantity > 0).all()

        jsonStock = StockJsonSchema(
            many = True,
            only=("id", "product_id", "warehouse_id", "quantity", "reserved_quantity")
        ).dump(stock)

        return {
            "stock": jsonStock
        }, 200
