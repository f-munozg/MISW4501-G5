from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from views.health_check import HealthCheck
from views.create_customer import CreateCustomer
from views.get_customer import GetCustomer
from views.get_customers import GetCustomers
from views.update_customer import UpdateCustomer
from views.assign_seller import AssignSeller
from views.create_payment import CreatePayment
from views.customers_by_seller import CustomersBySeller
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
    application.config["JWT_ACCESS_TOKEN_EXPIRES"] = False

    if not os.environ.get('TESTING'):
        init_db(application)

    add_routes(application)

    return application

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

def add_routes(application):
    api = Api(application)
    api.add_resource(HealthCheck, "/customers/ping") # GET
    api.add_resource(CreateCustomer, "/customers/customer") # POST
    api.add_resource(GetCustomer, "/customers/<user_id>") # GET
    api.add_resource(GetCustomers, "/customers") # GET
    api.add_resource(UpdateCustomer, "/customers/<user_id>") # PUT
    api.add_resource(AssignSeller, "/customers/assign_seller") # POST
    api.add_resource(CreatePayment, "/customers/payment") # POST
    api.add_resource(CustomersBySeller, "/customers/seller/<seller_id>") # GET

if __name__ == "__main__":
    application = create_app()
    port = int(os.environ.get('APP_PORT', 5001))
    application.run(host='0.0.0.0', port=port)