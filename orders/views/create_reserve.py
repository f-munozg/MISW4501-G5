import uuid, os, requests
from datetime import datetime
from models.models import db, Order, OrderProducts, Product
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from utils.call_stock_service import call_stock_service

class CreateReserve(Resource):
    def post(self):
        data = request.json

        required_fields = [
            "products", "user_id"
        ]

        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return {
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, 400
        
        try:
            uuid.UUID(data["user_id"])
        except: 
            return {"message": "invalid user id"}, 400
        
        if len(data.get("products")) == 0:
            return {"message": "empty product list"}, 400
                
        url_users = os.environ.get("CUSTOMERS_URL", "http://192.168.20.11:5001")
        user_id = data.get("user_id")
        url = f"{url_users}/customers/{user_id}"
        headers = {} #"Authorization": self.token}
        response = requests.request("GET", url, headers=headers)

        if response.status_code != 200:
            return response.json(), response.status_code

        customerId = response.json()["customer"]["id"]
        sellerId = response.json()["customer"]["assigned_seller"]

        previousReserves = db.session.query(Order).filter_by(customer_id=customerId, status="reserved").all()
        
        if len(previousReserves) > 0:
            return {
                "message": "customer already has a reserve"
            }, 409
        
        reserve = Order(
            customer_id = customerId,
            seller_id = sellerId,
            date_order = datetime.today(),
            status = "reserved"
        )

        try:
            db.session.add(reserve)
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
            return {
                "message": "missing field"
            }, 409

        order_total = 0
        delivery_date = datetime(1970,1,1,0,0)
        for product in data.get("products"):
            try:
                product_id = uuid.UUID(product["id"])
                quantity = int(product["quantity"])
            except:
                db.session.rollback()
                return {"message": "invalid product or quantity"}, 400

            item = db.session.query(Product).filter(Product.id == product_id).first()
            unit_value = item.unit_value
            order_total = round(order_total + (unit_value*quantity))
            if type(item.estimated_delivery_time) == datetime:
                delivery_date = max([delivery_date, item.estimated_delivery_time])

            # Llamar a stock para reservar
            status, resp = call_stock_service("/stock/reserve", {
                "product_id": str(product_id),
                "quantity": quantity,
                "user": user_id
            })
            if status != 200:
                db.session.rollback()
                return {"message": "Stock reservation failed", "details": resp}, status

            reserveProduct = OrderProducts(
                order_id = str(reserve.id),
                product_id = product["id"],
                quantity = product["quantity"],
                warehouse_id = uuid.UUID(resp["warehouse_id"])
            )
            db.session.add(reserveProduct)

        reserve.order_total = order_total
        reserve.date_delivery = delivery_date
        db.session.commit()

        return {
            "message": "reserve created successfully",
            "id": str(reserve.id)
        }, 201
