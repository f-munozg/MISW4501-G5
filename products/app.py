from flask import Flask
from flask_restful import Api
from models.models import db
from views.health_check import HealthCheck

import os

def create_app():
    application = Flask(__name__)

    add_routes(application)

    return application

def add_routes(application):
    api = Api(application)
    api.add_resource(HealthCheck, "/products/ping")

if __name__ == "__main__":
    application = create_app()
    application.run(host='0.0.0.0', port='5000')