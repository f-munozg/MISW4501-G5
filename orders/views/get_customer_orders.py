import uuid, os, requests
from models.models import db, Order, OrderJsonSchema
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

class GetCustomerOrders(Resource):
    def get(self, user_id):
        if not user_id or user_id == "":
            return {
                "message": "missing user id"
            }, 400

        try:
            uuid.UUID(user_id)
        except: 
            return {"message": "invalid user id"}, 400

        url_users = os.environ.get("CUSTOMERS_URL", "http://192.168.20.11:5001")
        url = f"{url_users}/customers/{user_id}"
        headers = {} #"Authorization": self.token}
        response = requests.request("GET", url, headers=headers)

        if response.status_code != 200:
            return response.json(), response.status_code

        customerId = response.json()["customer"]["id"]

        orders = db.session.query(Order).filter(Order.customer_id == customerId).all()

        jsonOrders = OrderJsonSchema(
            many = True,
        ).dump(orders)

        return {
            "orders": jsonOrders
        }, 200
