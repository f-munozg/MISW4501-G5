import uuid, os, requests
from models.models import db, Order, OrderJsonSchema, OrderProducts, Product, OrderProductsJsonSchema
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

class GetDetailedOrder(Resource):
    def get(self, order_id):

        if not order_id or order_id == "":
            return {
                "message": "missing order id"
            }, 400
        
        try:
            uuid.UUID(order_id)
        except: 
            return {"message": "invalid order id"}, 400

        order = db.session.query(Order).filter_by(id=order_id).first()
        if not order:
            return {
                "message": "order not found"
            }, 404

        order_products = OrderProductsJsonSchema(
            many=True
        ).dump(order.products)

        jsonOrder = OrderJsonSchema(
            only=  ("id", "customer_id", "seller_id", "date_order", "date_delivery", "status", "order_products")
        ).dump(order)

        return {
         "order": jsonOrder,
         "products": order_products
        }, 200
