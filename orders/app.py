from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
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
from views.add_payment import AddPayment
from views.pqrs import CustomerPQRS, SellerPQRS, GetPQRById, CreatePQR, UpdatePQR, DeletePQR

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
    api.add_resource(GetSellersWithOrders, "/orders/sellers_with_orders")
    api.add_resource(OptimizeOrder, "/orders/optimize")
    api.add_resource(AddPayment, "/orders/add_payment")

    api.add_resource(CustomerPQRS, "/orders/pqrs/getCustomer")
    api.add_resource(SellerPQRS, "/orders/pqrs/getSeller")
    api.add_resource(GetPQRById, '/orders/pqrs/<string:pqr_id>')
    api.add_resource(CreatePQR, "/orders/pqrs/addPQRS")
    api.add_resource(UpdatePQR, "/orders/pqrs/updatePQRS/<string:pqr_id>")
    api.add_resource(DeletePQR, "/orders/pqrs/deletePQRS/<string:pqr_id>")
    
def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    application = create_app()
    port = int(os.environ.get('APP_PORT', 5000))
    application.run(host='0.0.0.0', port=port)