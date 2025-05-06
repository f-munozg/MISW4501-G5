from datetime import datetime
from flask_restful import Resource

class SaveTruckLocation(Resource):
    def put(self, truck_id):
        # find truck
        # update data
        # return ok
        return "pong", 200
