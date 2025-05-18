from sqlalchemy import or_, and_
import uuid, os, requests
import random
from models.models import db, Order, PQR, PQRSType, PQRStatus, pqrs_schema, pqr_schema
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from datetime import datetime

class CustomerPQRS(Resource):
    def get(self):
        customer_id = request.args.get('customer_id')
        if not customer_id:
            return {"message": "customer_id is required"}, 400
        
        try:
            customer_uuid = uuid.UUID(customer_id)
        except ValueError:
            return {"message": "Invalid customer_id format"}, 400

        pqr_type = request.args.get('type')
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Validar tipo de PQR si se proporciona
        if pqr_type:
            try:
                pqr_type = PQRSType(pqr_type)
            except ValueError:
                valid_types = [e.value for e in PQRSType]
                return {"message": f"Invalid PQR type. Valid values: {valid_types}"}, 400

        # Validar estado si se proporciona
        if status:
            try:
                status = PQRStatus(status)
            except ValueError:
                valid_statuses = [e.value for e in PQRStatus]
                return {"message": f"Invalid PQR status. Valid values: {valid_statuses}"}, 400

        # Validar fechas
        if start_date or end_date:
            if not (start_date and end_date):
                return {"message": "Both start_date and end_date are required"}, 400
            
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                return {"message": "Invalid date format. Use YYYY-MM-DD"}, 400

        query = PQR.query.filter(PQR.customer_id == customer_id)
        
        if pqr_type:
            query = query.filter_by(type=pqr_type)
        if status:
            query = query.filter_by(status=status)
        if start_date and end_date:
            query = query.filter(
                PQR.created_at.between(start_date, end_date)
            )
        
        pqrs = query.all()
        return {"pqrs": pqrs_schema.dump(pqrs)}, 200

class SellerPQRS(Resource):
    def get(self):
        seller_id = request.args.get('seller_id')
        if not seller_id:
            return {"message": "seller_id is required"}, 400
        
        try:
            seller_uuid = uuid.UUID(seller_id)
        except ValueError:
            return {"message": "Invalid seller_id format"}, 400

        pqr_type = request.args.get('type')
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Validar tipo de PQR si se proporciona
        if pqr_type:
            try:
                pqr_type = PQRSType(pqr_type)
            except ValueError:
                valid_types = [e.value for e in PQRSType]
                return {"message": f"Invalid PQR type. Valid values: {valid_types}"}, 400

        # Validar estado si se proporciona
        if status:
            try:
                status = PQRStatus(status)
            except ValueError:
                valid_statuses = [e.value for e in PQRStatus]
                return {"message": f"Invalid PQR status. Valid values: {valid_statuses}"}, 400

        # Validar fechas
        if start_date or end_date:
            if not (start_date and end_date):
                return {"message": "Both start_date and end_date are required"}, 400
            
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                return {"message": "Invalid date format. Use YYYY-MM-DD"}, 400
        
        query = PQR.query.filter(PQR.seller_id == seller_id)
        
        if pqr_type:
            query = query.filter_by(type=pqr_type)
        if status:
            query = query.filter_by(status=status)
        if start_date and end_date:
            query = query.filter(
                PQR.created_at.between(start_date, end_date)
            )
        
        pqrs = query.all()
        return {"pqrs": pqrs_schema.dump(pqrs)}, 200

class GetPQRById(Resource):
    def get(self, pqr_id):
        # Obtener parámetros de identificación
        user_id = request.args.get('user_id')
        user_type = request.args.get('user_type')  # 'customer' o 'seller'
        
        if not user_id or not user_type:
            return {"message": "Missing user_id or user_type parameters"}, 400

        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            return {"message": "Invalid user ID format"}, 400

        # Cargar el PQR con relaciones
        pqr = PQR.query.options(
            joinedload(PQR.order)
        ).get(pqr_id)

        if not pqr:
            return {"message": "PQR not found"}, 404

        # Validar permisos según tipo de usuario
        if user_type == 'customer':
            if str(pqr.customer_id) != user_id:
                return {"message": "Access denied: Not the PQR owner"}, 403
        elif user_type == 'seller':
            if not pqr.order or str(pqr.order.seller_id) != user_id:
                return {"message": "Access denied: Not the assigned seller"}, 403
        else:
            return {"message": "Invalid user_type. Use 'customer' or 'seller'"}, 400

        # Construir respuesta
        response = {
            "pqr": {
                "id": str(pqr.id),
                "type": pqr.type.value,
                "title": pqr.title,
                "status": pqr.status.value,
                "created_at": pqr.created_at.isoformat(),
                "description": pqr.description,
                "amount": str(pqr.amount)
            },
            "related_data": {
                "order_id": str(pqr.order.id) if pqr.order else None,
                "customer_name": pqr.customer.username,
                "seller_name": pqr.seller.username if pqr.seller else None
            }
        }

        return response, 200

class CreatePQR(Resource): 
    def post(self):
        data = request.json
        
        required_fields = ["type", "title", "description", "order_id", "customer_id"]
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return {
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, 400
        
        try:
            order_uuid = uuid.UUID(data["order_id"])
            customer_uuid = uuid.UUID(data["customer_id"])
        except ValueError:
            return {"message": "Invalid UUID format"}, 400

        # Validar tipo de PQR
        try:
            pqr_type = PQRSType(data["type"])
        except ValueError:
            valid_types = [e.value for e in PQRSType]
            return {
                "message": f"Invalid PQR type. Valid values: {valid_types}"
            }, 400

        # Verificar que el order pertenece al cliente
        order_exists = db.session.query(
            Order.id
        ).filter(
            and_(
                Order.id == order_uuid,
                Order.customer_id == customer_uuid
            )
        ).first()
        
        if not order_exists:
            return {"message": "Order not found or doesn't belong to you"}, 404
        try:
            new_pqr = PQR(
                type=pqr_type,
                title=data["title"],
                description=data["description"],
                customer_id=data["customer_id"],
                order_id=data["order_id"]
            )
            
            db.session.add(new_pqr)
            db.session.commit()
            
            return {
                "message": "PQR created successfully",
                "pqr": pqr_schema.dump(new_pqr)
            }, 201
        except IntegrityError as e:
            db.session.rollback()
            return {"message": "Database error: " + str(e)}, 500
    
class UpdatePQR(Resource):
    def put(self, pqr_id):
        data = request.json
        
        if "order_id" not in data:
            return {"message": "order_id is required"}, 400

        # Validar formato de UUIDs
        try:
            pqr_uuid = uuid.UUID(str(pqr_id))
            order_uuid = uuid.UUID(str(data["order_id"]))
        except ValueError:
            return {"message": "Invalid UUID format"}, 400

        # Validar seller_id si está presente
        # if "seller_id" in data:
        #     try:
        #         seller_uuid = uuid.UUID(str(data["seller_id"]))
        #     except ValueError:
        #         return {"message": "Invalid seller ID format"}, 400

        # Validar status si está presente
        if "status" in data:
            try:
                status = PQRStatus(data["status"])
            except ValueError:
                valid_statuses = [e.value for e in PQRStatus]
                return {
                    "message": f"Invalid status. Valid values: {valid_statuses}"
                }, 400

        # Buscar el PQR primero
        pqr = PQR.query.get(pqr_uuid)
        if not pqr:
            return {"message": "PQR not found"}, 404

        # Luego buscar la orden
        order = Order.query.filter_by(id=order_uuid).first()
        if not order:
            return {"message": "Order not found"}, 404

        try:
            # Actualizar campos
            if "status" in data:
                pqr.status = status
            
            # if "seller_id" in data:
            #     pqr.seller_id = seller_uuid
            
            pqr.amount = round(random.uniform(0.1 * order.order_total, 0.9 * order.order_total), 2)
            
            try:
                db.session.commit()
            except IntegrityError as e:
                db.session.rollback()
                return {"message": "Database error: " + str(e)}, 500
            
            return {
                "message": "PQR updated successfully",
                "pqr": pqr_schema.dump(pqr)
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {"message": f"Server error: {str(e)}"}, 500

class DeletePQR(Resource):
    def delete(self, pqr_id):
        try:
            # Validar UUID
            pqr_uuid = uuid.UUID(str(pqr_id))
        except ValueError:
            return {"message": "Invalid UUID format"}, 400

        try:
            pqr = PQR.query.get(pqr_uuid)
            if not pqr:
                return {"message": "PQR not found"}, 404
            
            try:
                db.session.delete(pqr)
                db.session.commit()
            except IntegrityError as e:
                db.session.rollback()
                return {"message": "Database error: " + str(e)}, 500
            
            return {"message": "PQR deleted"}, 200
        except Exception as e:
            db.session.rollback()
            return {"message": f"Server error: {str(e)}"}, 500