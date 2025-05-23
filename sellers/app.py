from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from views.health_check import HealthCheck
from views.add_seller import AddSeller
from views.get_seller import GetSeller
from views.get_sellers import GetSellers
from views.get_sellers_by_ids import GetSellersByIds
from views.log_event import LogEvent
from models.models import db

import os, uuid

def create_app():
    application = Flask(__name__)
    CORS(application)

    host = os.environ.get('DB_HOST', 'localhost')
    port = os.environ.get('DB_PORT', '9432')
    dbName = os.environ.get('DB_NAME', 'maindb')
    username = os.environ.get('DB_USERNAME', 'postgres')
    password = os.environ.get('DB_PASSWORD', 'password')

    application.config["SQLALCHEMY_DATABASE_URI"] = f'postgresql://{username}:{password}@{host}:{port}/{dbName}'
    application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    application.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET_KEY', str(uuid.uuid4()))

    if not os.environ.get('TESTING'):
        init_db(application)

    add_routes(application)

    return application

def add_routes(application):
    api = Api(application)
    api.add_resource(HealthCheck, "/sellers/ping")
    api.add_resource(AddSeller, "/sellers/add")
    api.add_resource(GetSeller, "/sellers/seller")
    api.add_resource(GetSellers, "/sellers")
    api.add_resource(GetSellersByIds, "/sellers/sellers_by_ids")
    api.add_resource(LogEvent, "/sellers/log_event")

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    application = create_app()
    port = int(os.environ.get('APP_PORT', 4002))
    application.run(host='0.0.0.0', port=port)