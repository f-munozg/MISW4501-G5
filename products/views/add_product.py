from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from models.models import db, Product, ProductCategory
import uuid, random
from datetime import datetime


class AddProduct(Resource):
    # @jwt_required()
    def post(self):
        data = request.json

        required_fields = [
            "sku", "name", "unit_value", "storage_conditions",
            "product_features", "provider_id", "category"
        ]

        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        if missing_fields:
            return {
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, 400

        # Validar y convertir unit_value
        try:
            unit_value = float(data["unit_value"])
        except ValueError:
            return {"message": "unit_value must be a valid float"}, 400

        # Validar categoría
        try:
            category = ProductCategory[data["category"].upper()]
        except KeyError:
            valid = [cat.name for cat in ProductCategory]
            return {
                "message": f"Invalid category '{data['category']}'. Valid options are: {', '.join(valid)}"
            }, 400

        # Validar UUID de provider_id
        try:
            provider_id = uuid.UUID(data["provider_id"])
        except ValueError:
            return {"message": "provider_id must be a valid UUID"}, 400

        days_to_deliver = random.randint(1,5)
        estimated_delivery_time = datetime(1970, 1, days_to_deliver, 0, 0)
        
        product = Product(
            sku=data["sku"],
            name=data["name"],
            unit_value=unit_value,
            storage_conditions=data["storage_conditions"],
            product_features=data["product_features"],
            provider_id=provider_id,
            estimated_delivery_time=estimated_delivery_time,
            photo=data.get("photo"),
            description=data.get("description"),
            category=category
        )

        try:
            db.session.add(product)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"message": "Product is already registered"}, 409

        return {"message": "Product created successfully"}, 201
