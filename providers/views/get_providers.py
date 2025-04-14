import uuid, hashlib
from datetime import datetime
from models.models import db, Provider, ProviderJsonSchema
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

class GetProviders(Resource):
    def get(self):

        providers = db.session.query(Provider).all()

        jsonProviders = ProviderJsonSchema(
            many = True, only=("id", "name")
        ).dump(providers)

        return {
            "providers": jsonProviders
        }, 200