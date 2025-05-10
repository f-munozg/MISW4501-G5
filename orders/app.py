from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from models.models import db
from views.health_check import HealthCheck
from views.create_order import CreateOrder
from views.create_reserve import CreateReserve
from views.get_customer_orders import GetCustomerOrders
from views.get_order import GetOrder
from views.get_detailed_order import GetDetailedOrder
from views.get_orders import GetOrders
from views.update_order import UpdateOrderStatus
from views.get_orders_finished import GetOrdersFinished
from views.get_products_sold import GetProductsSold
from views.get_sellers_with_orders import GetSellersWithOrders
from views.optimize_order import OptimizeOrder
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
    application.config["JWT_ACCESS_TOKEN_EXPIRES"] = False

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
    api.add_resource(GetDetailedOrder, "/orders/<order_id>/detail")
    api.add_resource(CreateOrder, "/orders/order")
    api.add_resource(CreateReserve, "/orders/reserve")
    api.add_resource(UpdateOrderStatus, "/orders/updateStatus")
    api.add_resource(GetOrdersFinished, "/orders/orders_finished")
    api.add_resource(GetProductsSold, "/orders/products_sold")
    api.add_resource(GetSellersWithOrders, "/order/sellers_with_orders")
    api.add_resource(OptimizeOrder, "/orders/optimize")

if __name__ == "__main__":
    application = create_app()
    port = int(os.environ.get('APP_PORT', 5000))
    application.run(host='0.0.0.0', port=port)