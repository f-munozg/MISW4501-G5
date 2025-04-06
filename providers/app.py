from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from models.models import db
from views.health_check import HealthCheck
from views.add_provider import AddProvider

import os

def create_app():
    application = Flask(__name__)

    host = os.environ.get('DB_HOST', 'localhost')
    port = os.environ.get('DB_PORT', '5432')
    dbName = os.environ.get('DB_NAME', 'gcp_db')
    username = os.environ.get('DB_USERNAME', 'postgres')
    password = os.environ.get('DB_PASSWORD', 'Password123!')

    application.config["SQLALCHEMY_DATABASE_URI"] = f'postgresql://{username}:{password}@{host}:{port}/{dbName}'
    application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    application.config["JWT_SECRET_KEY"] = "frase-secreta"
    application.config["JWT_ACCESS_TOKEN_EXPIRES"] = False

    if not os.environ.get('TESTING'):
        init_db(application)

    add_routes(application)

    jwt = JWTManager(application)
    return application

def add_routes(application):
    api = Api(application)
    api.add_resource(HealthCheck, "/providers/ping")
    api.add_resource(AddProvider, "/providers/add")

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    application = create_app()
    port = int(os.environ.get('APP_PORT', 4000))
    application.run(host='0.0.0.0', port=port)