from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from models.models import db
from views.health_check import HealthCheck
from views.create_order import CreateOrder
from views.create_reserve import CreateReserve
from views.get_customer_orders import GetCustomerOrders
from views.get_order import GetOrder
from views.get_orders import GetOrders
from views.update_order import UpdateOrderStatus
import os, uuid

def create_app():
    application = Flask(__name__)

    host = os.environ.get('DB_HOST', 'localhost')
    port = os.environ.get('DB_PORT', '5432')
    dbName = os.environ.get('DB_NAME', 'gcp_db')
    username = os.environ.get('DB_USERNAME', 'postgres')
    password = os.environ.get('DB_PASSWORD', 'Password123!')

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
    api.add_resource(HealthCheck, "/orders/ping")
    api.add_resource(GetCustomerOrders, "/orders/user/<user_id>")
    api.add_resource(GetOrders, "/orders")
    api.add_resource(GetOrder, "/orders/<order_id>")
    api.add_resource(CreateOrder, "/orders/order")
    api.add_resource(CreateReserve, "/orders/reserve")
    api.add_resource(UpdateOrderStatus, "/order/updateStatus")

if __name__ == "__main__":
    application = create_app()
    port = int(os.environ.get('APP_PORT', 5000))
    application.run(host='0.0.0.0', port=port)