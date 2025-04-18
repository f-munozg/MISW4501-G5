import uuid, hashlib
from flask import request
from datetime import date
from sqlalchemy import and_, func, cast, Date
from sqlalchemy.orm import aliased
from models.models import db, Order, OrderProducts, Product, SalesJsonSchema
from flask_restful import Resource


class GetSales(Resource):
    def get(self):

        product_id = request.args.get('product')
        provider_id = request.args.get('provider')
        category = request.args.get('category')
        initial_date = request.args.get('initial_date')
        final_date = request.args.get('final_date')
        
        query = []
        if product_id and product_id != "":
            query.append(Product.id == product_id)
        if provider_id and provider_id != "":
            query.append(Product.provider_id == provider_id)
        if category and category != "":
            query.append(Product.category == category)
        if initial_date and final_date and initial_date != "" and final_date != "" and validate_date(initial_date) and validate_date(final_date):
            query.append(and_(Order.date_order <= final_date, Order.date_order >= initial_date))

        #products = db.session.query(Product, Order).join(OrderProducts, Product.id == OrderProducts.product_id).join(Order, Order.id == OrderProducts.order_id).all()
        query = db.session.query(
            Product.id,
            Product.name,
            func.sum(OrderProducts.quantity).label('total_quantity'),
            Product.unit_value,
            cast(Order.date_order, Date).label('purchase_date')
        ).join(
            OrderProducts, OrderProducts.product_id == Product.id
        ).join(
            Order, Order.id == OrderProducts.order_id
        ).filter(
            *query
        ).group_by(
            Product.id, Product.name, Product.unit_value, cast(Order.date_order, Date)
        )

        products = query.all()

        if len(products) == 0:
            return {
                "message": "not found"
            }, 204

        jsonProducts = SalesJsonSchema(
            many = True,
        ).dump(products)

        return jsonProducts, 200


def validate_date(date_text):
        try:
            date.fromisoformat(date_text)
            return True
        except ValueError:
            return False