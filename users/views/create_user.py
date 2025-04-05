import uuid, hashlib
from datetime import datetime
from models.models import db, User
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

class CreateUser(Resource):
    def post(self):
        data = request.json

        required_fields = [
            "username", "password", "email", "role"
        ]

        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return {
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, 400
        
        try:
            uuid.UUID(data["role"])
        except: 
            return {"message": "Invalid role ID"}, 400
        
        passwordToHash = str(data.get("password")).join(str(data.get("role")))
        pwd = hashlib.sha256(passwordToHash.encode()).hexdigest()
        
        newUser = User(
            username = data.get("username"),
            password = pwd,
            email = data.get("email"),
            role = data.get("role")
        )

        try:
            db.session.add(newUser)
            db.session.commit()
        except IntegrityError:
            return {
                "message": "user is already registered"
            }, 409

        
        return {
            "message": "user created successfully",
            "id": str(newUser.id)
        }, 201
