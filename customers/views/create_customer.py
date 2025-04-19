import uuid, hashlib, requests, os
from datetime import datetime
from models.models import db, Customer, Store, Role
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

class CreateCustomer(Resource):
    def post(self):
        data = request.json

        required_fields = [
            "username", "password", "email" 
        ]

        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return {
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, 400
        
        role = db.session.query(Role).filter_by(name="Cliente").first()

        user_creation = {
            "username": data.get("username"),
            "password": data.get("password"),
            "email": data.get("email"),
            "role": str(role.id)
        }

        url_users = os.environ.get("USERS_URL", "http://localhost:5010")
        url = f"{url_users}/users/user"
        headers = {} #"Authorization": self.token}
        body = user_creation
        response = requests.request("POST", url, headers=headers, json=body)

        if response.status_code != 201:
            return response.json(), response.status_code

        customer = Customer(
            user_id = response.json().get("id")
        )

        db.session.add(customer)
        db.session.commit()

        store = Store(
            customer_id = customer.id
        )

        db.session.add(store)
        db.session.commit()


        return {
            "message": "customer created successfully"
        }, 201