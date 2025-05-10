import uuid, os, requests
from datetime import datetime
from models.models import db, Order
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from utils.call_stock_service import call_stock_service

class CreateOrder(Resource):
    def post(self):
        data = request.json

        required_fields = [
            "user_id", "order_id"
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
        
        try:
            uuid.UUID(data["order_id"])
        except: 
            return {"message": "invalid order id"}, 400
        
        url_users = os.environ.get("CUSTOMERS_URL", "http://localhost:5001")
        user_id = data.get("user_id")
        url = f"{url_users}/customers/{user_id}"
        headers = {} #"Authorization": self.token}
        response = requests.request("GET", url, headers=headers)

        if response.status_code != 200:
            return response.json(), response.status_code

        customer_id = response.json()["customer"]["id"]
        
        order_id = data.get("order_id")

        order = db.session.query(Order).filter_by(customer_id=customer_id, id = order_id, status="reserved").first()

        if not order:
            return { "message": "invalid reserve to activate"}, 400
        
        for item in order.products:
            # Liberar reserva
            status1, res1 = call_stock_service("/stock/release", {
                "product_id": str(item.product_id),
                "warehouse_id": str(item.warehouse_id),
                "quantity": item.quantity,
                "user": user_id
            })
            if status1 != 200:
                db.session.rollback()
                return {"message": "Failed to release reserved stock", "details": res1}, status1

            # Registrar salida
            status2, res2 = call_stock_service("/stock/movement", {
                "product_id": str(item.product_id),
                "warehouse_id": str(item.warehouse_id),
                "quantity": item.quantity,
                "user": user_id,
                "movement_type": "SALIDA"
            })
            if status2 != 201:
                db.session.rollback()
                return {"message": "Failed to record stock movement", "details": res2}, status2

        order.status = "created"

        try:
            db.session.commit()
        except IntegrityError:
            return {
                "message": "order is already registered"
            }, 409

        return {
            "message": "order created successfully",
            "id": str(order.id),
            "estimated_delivery_date": str(order.date_delivery)
        }, 201
