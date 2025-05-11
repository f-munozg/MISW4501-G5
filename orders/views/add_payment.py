import uuid, os, requests
from datetime import datetime
from models.models import db, Order, Payments
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from utils.ocr_image_payment import extract_amount_from_image

class AddPayment(Resource):
    def post(self):        
        data = request.json

        required_fields = ["order_id", "receipt_image"]

        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return {
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, 400
        
        try:
            order_id = uuid.UUID(data['order_id'])
        except ValueError:
            return {"message": "ID de orden inválido"}, 400
        
        order = Order.query.get(order_id)
        if not order:
            return {"message": "Orden no encontrada"}, 404
        
        if order.status == "paid":
            return {
                "message": "La orden ya está completamente pagada",
            }, 400
        
        payment_amount = extract_amount_from_image(data['receipt_image'])
        if not payment_amount:
            return {"message": "No se pudo determinar el monto pagado"}, 400
        
        if payment_amount <= 0:
            return {
                "message": "El monto pagado debe ser mayor a cero"
            }, 400
        
        total_paid = db.session.query(
            db.func.coalesce(db.func.sum(Payments.payment), 0.0)
        ).filter(Payments.order_id == order_id).scalar() + payment_amount
        
        if total_paid > order.order_total:
            return {
                "message": f"El pago excede el total de la orden. Total: {order.order_total}, Pagado: {total_paid}"
            }, 400
        
        remaining_balance = order.order_total - total_paid
        
        new_payment = Payments(
            order_id=order_id,
            total=order.order_total,
            payment=payment_amount,
            balance=remaining_balance,
            payment_date=datetime.utcnow()
        )
        try:
            db.session.add(new_payment)
            
            if total_paid == order.order_total:
                order.status_payment = "paid"
            elif total_paid > 0:
                order.status_payment = "partial payment"
            
            db.session.commit()
            
            payment_history = Payments.query.filter_by(order_id=order_id)\
                .order_by(Payments.payment_date.asc()).all()

            return {
                "message": "Pago registrado exitosamente",
                "payment_id": str(new_payment.id),
                "order_id": str(order_id),
                "current_payment": payment_amount,
                "total_paid": total_paid,
                "remaining_balance": remaining_balance,
                "order_status_payment": order.status_payment,
                "payment_history": [
                    {
                        "payment_id": str(p.id),
                        "amount": p.payment,
                        "date": p.payment_date.isoformat(),
                        "balance_after": p.balance
                    } for p in payment_history
                ]
            }, 201
        
        except IntegrityError as e:
                db.session.rollback()
                return {
                    "message": "Error al registrar el pago en la base de datos",
                    "details": str(e)
                }, 500