import uuid, requests, os, base64
from datetime import datetime
from models.models import db, Payment, MeansOfPayment, TypeOfPayment
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.postgresql import UUID

class CreatePayment(Resource):
    def post(self):
        data = request.json

        required_fields = [
            "order_id", "type_payment", "mean_payment", "voucher_payment"
        ]

        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return {
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, 400

        try:
            order_id = uuid.UUID(data["order_id"])
        except ValueError:
            return {"message": "Invalid order_id format"}, 400

        order_url_base = os.environ.get("ORDERS_URL", "http://localhost:5000")
        order_url = f"{order_url_base}/orders/{order_id}"
        order_response = requests.get(order_url)

        if order_response.status_code != 200:
            return {"message": "Invalid or non-existent order_id"}, 404
        


        try:
            type_payment = TypeOfPayment[data["type_payment"].upper()]
            mean_payment = MeansOfPayment[data["mean_payment"].upper().replace(" ", "_")]
        except KeyError:
            return {"message": "Invalid type_payment or mean_payment"}, 400

        try:
            base64.b64decode(data["voucher_payment"], validate=True)
        except Exception:
            return {"message": "Invalid base64 format for voucher_payment"}, 400

        payment = Payment(
            order_id=order_id,
            date_payment=datetime.now,
            type_payment=type_payment,
            mean_payment=mean_payment,
            voucher_payment=data["voucher_payment"]
        )
        
        order_data = order_response.json()
        order_data["status"] = "Pagado"
        order_update_url = f"{order_url_base}/orders/updateStatus"
        update_response = requests.put(order_update_url, json=order_data)

        if update_response.status_code != 200:
            return {"message": "Failed to update order status"}, 500

        if order_response.status_code != 200:
            return {"message": "Invalid or non-existent order_id"}, 404

        try:
            db.session.add(payment)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"message": "Error saving payment, possibly duplicate or DB error"}, 500

        return {"message": "Payment created successfully"}, 201
