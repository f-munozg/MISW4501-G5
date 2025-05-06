from datetime import datetime
from flask_restful import Resource

class RegisterTruckLocation(Resource):
    def post(self, truck_id):
        # validate data
        # send to topic
        return "pong", 200
