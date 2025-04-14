import uuid, os, requests
from datetime import datetime
from models.models import db, Order, OrderProducts
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

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
        
        
        url_users = os.environ.get("CUSTOMERS_URL", "http://localhost:5001")
        user_id = data.get("user_id")
        url = f"{url_users}/customers/{user_id}"
        headers = {} #"Authorization": self.token}
        response = requests.request("GET", url, headers=headers)

        if response.status_code != 200:
            return response.json(), response.status_code

        customerId = response.json()["customer"]["id"]
        sellerId = data.get("seller_id")

        previousReserves = db.session.query(Order).filter_by(customer_id=customerId, status="reserved").all()
        
        if len(previousReserves) > 0:
            return {
                "message": "customer already has a reserve"
            }, 409
        
        reserve = Order(
            customer_id = customerId,
            seller_id = sellerId,
            date_order = datetime.today(),
            date_delivery = datetime.today(),
            status = "reserved"
        )

        try:
            db.session.add(reserve)
            db.session.commit()
        except IntegrityError:
            return {
                "message": "missing field"
            }, 409

        for product in data.get("products"):
            reserveProduct = OrderProducts(
                order_id = str(reserve.id),
                product_id = product["id"],
                quantity = product["quantity"]
            )
            db.session.add(reserveProduct)
        
        db.session.commit()

        return {
            "message": "reserve created successfully",
            "id": str(reserve.id)
        }, 201
