import uuid, os, requests
from datetime import datetime
from models.models import db, Order, OrderProducts
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

class CreateOrder(Resource):
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
        
        
        url_users = os.environ.get("CUSTOMERS_URL", "http://localhost:5001")
        url = f"{url_users}/customers/{data.get("user_id")}"
        headers = {} #"Authorization": self.token}
        response = requests.request("GET", url, headers=headers)

        if response.status_code != 200:
            return response.json(), response.status_code

        customer_id = response.json()["customer"]["id"]
        seller_id = data.get("seller_id")
        
        order = Order(
            customer_id = customer_id,
            seller_id = seller_id,
            date_order = datetime.today(),
            date_delivery = datetime.today(),
            status = "created"
        )

        try:
            db.session.add(order)
            db.session.commit()
        except IntegrityError:
            return {
                "message": "order is already registered"
            }, 409

        for product in data.get("products"):
            orderProduct = OrderProducts(
                order_id = str(order.id),
                product_id = product["id"],
                quantity = product["quantity"]
            )
            db.session.add(orderProduct)
        
        db.session.commit()

        return {
            "message": "order created successfully",
            "id": str(order.id),
            "estimated_delivery_date": str(order.date_delivery)
        }, 201
