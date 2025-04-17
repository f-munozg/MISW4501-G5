from flask import Flask
from flask_restful import Api
from views.health_check import HealthCheck
from views.add_product import AddProduct
from views.get_products import GetProducts
from views.get_provider_products import GetProviderProducts
from views.add_file_product import FileUploadProducts
from models.models import db
import os

def create_app():
    application = Flask(__name__)

    host = os.environ.get('DB_HOST', 'localhost')
    port = os.environ.get('DB_PORT', '9432')
    dbName = os.environ.get('DB_NAME', 'maindb')
    username = os.environ.get('DB_USERNAME', 'postgres')
    password = os.environ.get('DB_PASSWORD', 'password')

    application.config["SQLALCHEMY_DATABASE_URI"] = f'postgresql://{username}:{password}@{host}:{port}/{dbName}'
    application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    application.config["JWT_SECRET_KEY"] = "frase-secreta"
    application.config["JWT_ACCESS_TOKEN_EXPIRES"] = False

    if not os.environ.get('TESTING'):
        init_db(application)

    add_routes(application)

    return application

def add_routes(application):
    api = Api(application)
    api.add_resource(HealthCheck, "/products/ping")
    api.add_resource(AddProduct, "/products/add")
    api.add_resource(GetProducts, "/products")
    api.add_resource(FileUploadProducts, "/products/upload")
    api.add_resource(GetProviderProducts, "/products/provider/<provider_id>")

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    application = create_app()
    port = int(os.environ.get('APP_PORT', 4001))
    application.run(host='0.0.0.0', port=port)