from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from models.models import db, Seller, Role
import uuid, hashlib, requests, os

class AddSeller(Resource):
    def post(self):
        data = request.json

        identification_number = data.get("identification_number")
        email = data.get("email")

        required_fields = [
            "identification_number", "email", "name"]

        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return {
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, 400
        
        zone = data.get("zone")
        if zone:
            zone = zone.upper()
            valid_zones = {"NORTE", "SUR", "ORIENTE", "OCCIDENTE"}
            if zone not in valid_zones:
                return {"message": f"Invalid zone '{zone}'. Must be one of: {', '.join(valid_zones)}"}, 400
        else:
            return {"message": "Missing required field: zone"}, 400

        role = db.session.query(Role).filter_by(name="Vendedor").first()

        user_creation = {
            "username": data.get("username"),
            "password": data.get("password"),
            "email": data.get("email"),
            "role": str(role.id)
        }

        url_users = os.environ.get("USERS_URL", "http://localhost:5000")
        url = f"{url_users}/users/user"
        headers = {} #"Authorization": self.token}
        body = user_creation
        response = requests.request("POST", url, headers=headers, json=body)

        if response.status_code != 201:
            return response.json(), response.status_code

        seller = Seller(
            user_id = response.json().get("id"),
            identification_number=identification_number,
            name=data.get("name"),
            email=email,
            address=data.get("address"),
            phone=data.get("phone"),
            zone=zone
        )

        try:
            db.session.add(seller)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"message": "Seller is already registered"}, 409

        return {"message": "Seller created successfully"}, 201
