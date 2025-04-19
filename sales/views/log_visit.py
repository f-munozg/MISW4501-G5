import uuid, hashlib, os, requests
from datetime import datetime
from models.models import db, Visit
from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError

class LogVisit(Resource):
    def post(self):
        data = request.json

        required_fields = [
            "user_id", "customer_id", "store_address", "zone", "visit_status"
        ]

        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return {
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, 400
        
        seller_user_id = data.get("user_id")
        try:
            uuid.UUID(seller_user_id)
        except: 
            return {"message": "invalid user id"}, 400
        
        url_sellers = os.environ.get("SELLERS_URL", "http://localhost:4002")
        url = f"{url_sellers}/sellers/seller?user_id={seller_user_id}"
        headers = {} #"Authorization": self.token}
        response = requests.request("GET", url, headers=headers)

        if response.status_code != 200:
            return response.json(), response.status_code

        seller_id = response.json()["seller"]["id"]

        visit = Visit(
            seller_id = seller_id,
            customer_id = data.get("customer_id"),
            store_address = data.get("store_address"),
            zone = data.get("zone"),
            visit_status = data.get("visit_status"),
            visit_result = data.get("visit_result"),
            observations = data.get("observations")
        )

        db.session.add(visit)
        db.session.commit()

        return {
            "message": "log successful"
        }, 201
