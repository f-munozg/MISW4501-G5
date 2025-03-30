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
                "message": "provider is already blacklisted"
            }, 409

        return {
            "message": "provider created successfully"
        }, 201