from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models.models import db, Role, RoleJsonSchema
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

class GetRoles(Resource):
    #@jwt_required()
    def get(self):
        #current_user = get_jwt_identity()

        roles = db.session.query(Role).all()

        jsonRoles = RoleJsonSchema(
            many = True,
        ).dump(roles)

        return {
            "roles": jsonRoles
        }, 200
