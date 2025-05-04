from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from models.models import db, Product, ProductCategory
import uuid
from datetime import datetime

class UpdateProduct(Resource):
    def put(self, product_id):
        data = request.json

        try:
            product_uuid = uuid.UUID(product_id)
        except ValueError:
            return {"message": "Invalid product ID"}, 400

        product = db.session.query(Product).filter_by(id=product_uuid).first()
        if not product:
            return {"message": "Product not found"}, 404

        updatable_fields = [
            "sku", "name", "unit_value", "storage_conditions",
            "product_features", "provider_id", "category",
            "estimated_delivery_time", "photo", "description"
        ]

        if "unit_value" in data:
            try:
                product.unit_value = float(data["unit_value"])
            except ValueError:
                return {"message": "unit_value must be a valid float"}, 400

        if "category" in data:
            try:
                product.category = ProductCategory[data["category"].upper()]
            except KeyError:
                valid = [cat.name for cat in ProductCategory]
                return {
                    "message": f"Invalid category '{data['category']}'. Valid options are: {', '.join(valid)}"
                }, 400

        if "provider_id" in data:
            try:
                product.provider_id = uuid.UUID(data["provider_id"])
            except ValueError:
                return {"message": "provider_id must be a valid UUID"}, 400

        if "estimated_delivery_time" in data:
            try:
                product.estimated_delivery_time = datetime.fromisoformat(data["estimated_delivery_time"])
            except ValueError:
                return {"message": "Invalid format for 'estimated_delivery_time'. Use ISO format (YYYY-MM-DDTHH:MM:SS)."}, 400

        for field in updatable_fields:
            if field in data and field not in ["unit_value", "category", "provider_id", "estimated_delivery_time"]:
                setattr(product, field, data[field])

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"message": "Error updating product. Possibly duplicate SKU or invalid data."}, 400

        return {"message": "Product updated successfully"}, 202
