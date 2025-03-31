from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from models.models import db, Product

class AddProduct(Resource):
    # @jwt_required()
    def post(self):
        data = request.json

        required_fields = [
            "sku", "name", "unit_value", "conditions_storage",
            "product_features", "provider_id", "time_delivery_dear", "photo", "description"
        ]

        # Verificar si algún campo obligatorio falta
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return {
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, 400

        product = Product (
            sku = data.get("sku"),
            name = data.get("name"),
            unit_value = data.get("unit_value"),
            conditions_storage = data.get("conditions_storage"),
            product_features = data.get("product_features"),
            provider_id = data.get("provider_id"),
            time_delivery_dear = data.get("time_delivery_dear"),
            photo = data.get("photo"),           
            description = data.get("description")
        )
        try:
            db.session.add(product)
            db.session.commit()
        except IntegrityError:
            return {
                "message": "product is already registered"
            }, 409

        return {
            "message": "product created successfully"
        }, 201