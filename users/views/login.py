import uuid, hashlib
from datetime import datetime
from models.models import db, User, Role, Privilege, Role_Privilege, PrivilegeJsonSchema
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

class LoginUser(Resource):
    def post(self):
        data = request.json

        required_fields = [
            "username", "password"
        ]

        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return {
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, 400
        

        storedUser = db.session.query(User).filter_by(username=data.get("username")).first()

        if not storedUser:
            return {
                "message": "invalid username or password"
            }, 401


        passwordToHash = str(data.get("password")).join(str(storedUser.role))
        pwd = hashlib.sha256(passwordToHash.encode()).hexdigest()
        
        if pwd != storedUser.password:
            return {
                "message": "invalid username or password"
            }, 401
        
        role = db.session.query(Role).filter_by(id=storedUser.role).first()

        privileges = db.session.query(Privilege).join(Role_Privilege, Privilege.id == Role_Privilege.privilege_id, isouter=True).filter_by(role_id= role.id).all()

        print('privileges:', privileges)

        jsonPrivileges = PrivilegeJsonSchema(
            many = True,
        ).dump(privileges)

        print('json privileges:', jsonPrivileges)

        return {
            "message": "login successful",
            "role": role.name,
            "privileges": jsonPrivileges,
            "user_id": str(storedUser.id)
        
        }, 200
