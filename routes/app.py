from flask import Flask
from flask_restful import Api
from views.health_check import HealthCheck
from views.get_trucks import GetTrucks
from views.get_trucks_location import GetTrucksLocation
from views.get_delivery_location import GetDeliveryLocation
from views.get_route_detail import GetRouteDetail
from views.create_route_delivery import CreateRouteDelivery
from views.create_route_sales import CreateRouteSales
from views.update_route import UpdateRoute
from views.confirm_route import ConfirmRoute
from views.update_stop import UpdateStop
from views.register_truck_location import RegisterTruckLocation
from views.save_truck_location import SaveTruckLocation
from views.get_routes import GetRoutes
from views.get_stops_by_customer import GetStopsByCustomer
from views.create_truck import CreateTruck
from views.update_truck import UpdateTruck
from views.get_stops import GetStops
from views.register_visit import RegisterVisit
from models.models import db

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

    return application

def add_routes(application):
    api = Api(application)
    api.add_resource(HealthCheck, "/routes/ping")
    api.add_resource(GetTrucks, "/routes/trucks") # GET consultar camiones
    api.add_resource(GetTrucksLocation, "/routes/trucks/location") # GET Consultar ubicación camiones
    api.add_resource(CreateTruck, "/routes/truck")
    api.add_resource(UpdateTruck, "/routes/truck")
    api.add_resource(RegisterTruckLocation, "/routes/truck/<truck_id>/location") # POST registrar ubicación
    api.add_resource(SaveTruckLocation, "/routes/truck/location") # POST actualizar ubicación

    api.add_resource(GetDeliveryLocation, "/routes/<order_id>/location")# GET consultar ubicación pedido
    api.add_resource(GetRoutes, "/routes") # GET consultar rutas
    api.add_resource(GetRouteDetail, "/routes/<route_id>")# GET consultar ruta (Vendedor | camión)
    api.add_resource(CreateRouteDelivery, "/routes/delivery")# POST crear rutas camiones
    api.add_resource(CreateRouteSales, "/routes/seller") # POST crear ruta vendedor
    api.add_resource(UpdateRoute, "/routes/<route_id>/update") # PUT actualizar ruta
    api.add_resource(ConfirmRoute, "/routes/<route_id>/confirm") # PUT confirmar ruta
    
    api.add_resource(UpdateStop, "/routes/stop/<stop_id>") # POST actualizar parada
    api.add_resource(RegisterVisit, "/routes/stop/store") # POST registrar visita
    api.add_resource(GetStops, "/routes/stops") # GET consultar todas las paradas
    api.add_resource(GetStopsByCustomer, "/routes/stops/customer/<customer_id>") # GET consultar visitas a cliente
    

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    application = create_app()
    port = int(os.environ.get('APP_PORT', 5005))  # Puerto 5005 para routes
    application.run(host='0.0.0.0', port=port)