import uuid
from models.models import db, Order, OrderJsonSchema, Payments, PaymentSummarySchema
from flask import request
from flask_restful import Resource
from sqlalchemy import desc

class GetOrder(Resource):
    def get(self, order_id):
        if not order_id or order_id == "":
            return {"message": "missing order id"}, 400
        
        try:
            uuid.UUID(order_id)
        except: 
            return {"message": "invalid order id"}, 400

        order = db.session.query(Order).filter_by(id=order_id).first()
        if not order:
            return {
                "message": "order not found"
            }, 404

        last_payment = db.session.query(Payments)\
            .filter(Payments.order_id == order_id)\
            .order_by(desc(Payments.payment_date))\
            .first()

        if last_payment:
            payment_summary = {
                "total_amount": last_payment.total,
                "paid_amount": last_payment.total - last_payment.balance,
                "pending_balance": last_payment.balance,
                "last_payment_date": last_payment.payment_date
            }
        else:
            payment_summary = {
                "total_amount": order.order_total,
                "paid_amount": 0.0,
                "pending_balance": order.order_total,
                "last_payment_date": None
            }

        json_order = OrderJsonSchema(
            only=("id", "customer_id", "seller_id", "date_order", "date_delivery", "status", "order_total", "status_payment",)
        ).dump(order)

        payment_summary_schema = PaymentSummarySchema()

        return {
            "order": json_order,
            "payment_summary": payment_summary_schema.dump(payment_summary)
        }, 200