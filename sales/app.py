from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from models.models import db
from views.get_sales import GetSales
from views.definition_sales_plan import DefinitionSalesPlan
from views.health_check import HealthCheck
from views.log_visit import LogVisit
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

    jwt = JWTManager(application)
    return application

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

def add_routes(application):
    api = Api(application)
    api.add_resource(HealthCheck, "/sales/ping")
    api.add_resource(GetSales, "/sales")
    api.add_resource(DefinitionSalesPlan, "/sales-plans", endpoint="sales_plans")
    api.add_resource(LogVisit, "/sales/log-visit")

if __name__ == "__main__":
    application = create_app()
    port = int(os.environ.get('APP_PORT', 5006))
    application.run(host='0.0.0.0', port=port)