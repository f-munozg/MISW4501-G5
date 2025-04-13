import uuid, os, requests
from datetime import datetime
from models.models import db, Provider, ProviderJsonSchema
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

class GetProvider(Resource):
    def get(self, provider_id):
        if not provider_id or provider_id == "":
            return {
                "message": "missing provider id"
            }, 400

        try:
            uuid.UUID(provider_id)
        except: 
            return {"message": "invalid provider id"}, 400
        
        provider = db.session.query(Provider).filter_by(id = provider_id).first()

        if not provider:
            return {
                "message": "provider not found"
            }, 404
        
        url_products = os.environ.get("PRODUCTS_URL", "http://localhost:4001")
        url = f"{url_products}/products/provider/{provider_id}"
        headers = {} #"Authorization": self.token}
        response = requests.request("GET", url, headers=headers)

        if response.status_code != 200:
            return response.json(), response.status_code
        

        jsonProvider = ProviderJsonSchema().dump(provider)

        products = response.json().get("products")

        return {
            "provider": jsonProvider,
            "portfolio": products

        }, 200
