from datetime import datetime
from flask_restful import Resource

class HealthCheck(Resource):
    def get(self):
        return "pong", 200
