import os
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from views.health_check import HealthCheck
from views.report_sales import (
    ReporteVentas, 
    ReporteVentasCSV, 
    ReporteVentasExcel
)
from views.report_seller import (
    ReporteVendedor,
    ReporteVendedorCSV,
    ReporteVendedorExcel
)

def create_app():
    application = Flask(__name__)

    add_routes(application)

    jwt = JWTManager(application)
    return application

def add_routes(application):
    api = Api(application)
    api.add_resource(HealthCheck, "/reports/ping")
    api.add_resource(ReporteVentas, "/reports/reporte_ventas")
    api.add_resource(ReporteVentasCSV, "/reports/reporte_ventas_csv")
    api.add_resource(ReporteVentasExcel, "/reports/reporte_ventas_excel")
    
    api.add_resource(ReporteVendedor, "/reports/reporte_vendedor")
    api.add_resource(ReporteVendedorCSV, "/reports/reporte_vendedor_csv")
    api.add_resource(ReporteVendedorExcel, "/reports/reporte_vendedor_excel")

if __name__ == "__main__":
    application = create_app()
    port = int(os.environ.get('APP_PORT', 5004))  # Puerto 5004 para reports
    application.run(host='0.0.0.0', port=port)