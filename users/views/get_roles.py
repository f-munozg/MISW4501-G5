import uuid, hashlib
from datetime import datetime
from models.models import db, Role, RoleJsonSchema
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

class GetRoles(Resource):
    def get(self):

        roles = db.session.query(Role).all()

        jsonRoles = RoleJsonSchema(
            many = True,
        ).dump(roles)

        return {
            "roles": jsonRoles
        }, 200
