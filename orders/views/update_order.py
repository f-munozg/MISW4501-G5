from flask_restful import Resource, reqparse
from flask import request
from models.models import db, Order
import uuid

class UpdateOrderStatus(Resource):
    def put(self):
        try:
            data = request.get_json()

            # Validar campos requeridos
            order_id = data.get("order_id")
            status = data.get("status")

            if not order_id or not status:
                return {"message": "order_id and status are required"}, 400

            # Validar UUID
            try:
                order_uuid = uuid.UUID(order_id)
            except ValueError:
                return {"message": "Invalid order ID format"}, 400

            # Buscar orden
            order = Order.query.get(order_uuid)
            if not order:
                return {"message": "Order not found"}, 404

            # Actualizar estado
            order.status = status
            db.session.commit()

            return {"message": "Order status updated successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"message": f"An error occurred: {str(e)}"}, 500
