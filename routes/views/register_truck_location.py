import os, json
from flask import request
from datetime import datetime
from flask_restful import Resource
from google.cloud import pubsub_v1

class RegisterTruckLocation(Resource):
    def post(self):
        data = request.get_json()
        publishLocationUpdateMessage(data)

        # Return an HTTP response
        return 'OK'

def publishLocationUpdateMessage(data) -> None:
    project_id =  os.environ.get("PROJECT_NAME", "MISW4502-G5-ProyectoFinal1")
    topic_id = os.environ.get("TOPIC_ID_LOCATION_UPDATE", "location-update")

    message = json.dumps(data).encode('utf-8')
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    future = publisher.publish(topic_path, data=message)
    print(future.result())