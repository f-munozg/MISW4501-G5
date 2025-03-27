from datetime import datetime
from flask_restful import Resource
from models.models import db

class HealthCheck(Resource):
    def get(self):
        return "pong", 200
