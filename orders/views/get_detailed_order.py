import uuid, os, requests
from models.models import db, Order, OrderJsonSchema, Product, ProductJsonSchema
from flask import request
from flask_restful import Resource

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

        products = db.session.query(Product).filter(Product.id.in_([order.product_id for order in order.products])).all()
        
        op = {o.product_id: o for o in order.products}
        order_products = []
        print(op, flush=True)
        for product in products:
            p = ProductJsonSchema().dump(product)
            order_products.append({
                "product": p,
                "quantity": op[product.id].quantity
            })

        jsonOrder = OrderJsonSchema(
            only=  ("id", "customer_id", "seller_id", "date_order", "date_delivery", "status")
        ).dump(order)

        return {
         "order": jsonOrder,
         "products": order_products
        }, 200
