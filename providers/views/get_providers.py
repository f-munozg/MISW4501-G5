import uuid, hashlib
from datetime import datetime
from models.models import db, Provider, ProviderJsonSchema
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

class GetProviders(Resource):
    def get(self):

        providers = db.session.query(Provider).all()

        jsonCustomers = ProviderJsonSchema(
            many = True,
        ).dump(providers)

        return {
            "providers": jsonCustomers
        }, 200
