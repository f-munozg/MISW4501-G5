from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from models.models import db
from views.health_check import HealthCheck
from views.add_provider import AddProvider
from views.get_providers import GetProviders
from views.get_provider import GetProvider
from views.add_tax_rule import AddTaxRule

import os, uuid

def create_app():
    application = Flask(__name__)

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

    jwt = JWTManager(application)
    return application

def add_routes(application):
    api = Api(application)
    api.add_resource(HealthCheck, "/providers/ping")
    api.add_resource(AddProvider, "/providers/add")
    api.add_resource(GetProvider, "/providers/<provider_id>")
    api.add_resource(GetProviders, "/providers")
    api.add_resource(AddTaxRule, "/rules/tax/add")

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    application = create_app()
    port = int(os.environ.get('APP_PORT', 4000))
    application.run(host='0.0.0.0', port=port)
