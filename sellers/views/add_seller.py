from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from models.models import db, Seller

class AddSeller(Resource):
    def post(self):
        data = request.json

        identification_number = data.get("identification_number")
        email = data.get("email")

        required_fields = [
            "identification_number", "email", "name"]

        # Verificar si algún campo obligatorio falta
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return {
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, 400

        # existing_seller = Seller.query.filter(
        #     (Seller.identification_number == identification_number) | (Seller.email == email)
        # ).first()

        # if existing_seller:
        #     return {
        #         "message": "Either the identification number or email already exists"
        #     }, 409

        seller = Seller(
            identification_number=identification_number,
            name=data.get("name"),
            email=email,
            address=data.get("address"),
            phone=data.get("phone"),
            zone=data.get("zone")
        )

        try:
            db.session.add(seller)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"message": "Seller is already registered"}, 409

        return {"message": "Seller created successfully"}, 201
