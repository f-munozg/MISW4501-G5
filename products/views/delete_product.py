from flask import request
from flask_restful import Resource
from models.models import db, Product
import uuid

class DeleteProduct(Resource):
    def delete(self, product_id):
        try:
            product_uuid = uuid.UUID(product_id)
        except ValueError:
            return {"message": "Invalid product ID"}, 400

        product = db.session.query(Product).filter_by(id=product_uuid).first()
        if not product:
            return {"message": "Product not found"}, 404

        db.session.delete(product)
        db.session.commit()

        return {"message": "Product deleted successfully"}, 200
