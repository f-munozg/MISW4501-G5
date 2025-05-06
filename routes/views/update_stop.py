from datetime import datetime
from flask_restful import Resource

class UpdateStop(Resource):
    def post(self, stop_id):
        # validate data
        # find stop
        # update data
        # save
        # if last stop, finish route
        # if delivery, update order
        return "pong", 200
