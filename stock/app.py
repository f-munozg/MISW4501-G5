from flask import Flask
from flask_restful import Api
from views.health_check import HealthCheck
from views.stock_query import StockyQuery
from views.product_stock_location import ProductStockLocation
from views.product_with_stock import ProductWithStock
from views.stock_movements import StockMovement
from models.models import db

import os, uuid

def create_app():
    application = Flask(__name__)

    # host = os.environ.get('DB_HOST', 'localhost')
    # port = os.environ.get('DB_PORT', '5432')
    # dbName = os.environ.get('DB_NAME', 'gcp_db')
    # username = os.environ.get('DB_USERNAME', 'postgres')
    # password = os.environ.get('DB_PASSWORD', 'Password123!')

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
    api.add_resource(HealthCheck, "/stock/ping")
    api.add_resource(StockyQuery, "/stock/query")
    api.add_resource(ProductStockLocation, "/stock/product_location")
    api.add_resource(ProductWithStock, "/stock/get")
    api.add_resource(StockMovement, "/stock/movement")

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    application = create_app()
    port = int(os.environ.get('APP_PORT', 4003))
    application.run(host='0.0.0.0', port=port)