from datetime import datetime
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from models.models import db, Provider

class AddProvider(Resource):
    # @jwt_required()
    def post(self):
        data = request.json

        required_fields = [
            "identification_number", "name", "address", "countries",
            "identification_number_contact", "name_contact", "phone_contact", "address_contact"
        ]

        # Verificar si algún campo obligatorio falta
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return {
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, 400

        # Validar tipos de datos básicos
        if not isinstance(data["identification_number"], str) or not data["identification_number"].isdigit():
            return {"message": "Invalid 'identification_number'. Must be a numeric string."}, 400

        if not isinstance(data["phone_contact"], str) or not data["phone_contact"].isdigit():
            return {"message": "Invalid 'phone_contact'. Must be a numeric string."}, 400

        provider = Provider(
            identification_number = data.get("identification_number"),
            name = data.get("name"),
            address = data.get("address"),
            countries = data.get("countries"),
            identification_number_contact = data.get("identification_number_contact"),
            name_contact = data.get("name_contact"),
            phone_contact = data.get("phone_contact"),
            address_contact = data.get("address_contact")            
        )
        try:
            db.session.add(provider)
            db.session.commit()
        except IntegrityError:
            return {
                "message": "provider is already registered"
            }, 409

        return {
            "message": "provider created successfully"
        }, 201