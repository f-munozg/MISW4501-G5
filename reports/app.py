import uuid, os
from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from views.health_check import HealthCheck
from views.report_sales import ReporteVentas, ReporteVentasCSV, ReporteVentasExcel, ReporteVentasPDF

import os

def create_app():
    application = Flask(__name__)
    CORS(application)

    add_routes(application)

    jwt = JWTManager(application)
    return application

def add_routes(application):
    api = Api(application)
    api.add_resource(HealthCheck, "/reports/ping")
    api.add_resource(ReporteVentas, "/reports/reporte_ventas")
    api.add_resource(ReporteVentasCSV, "/reports/reporte_ventas_csv")
    # api.add_resource(ReporteVentasPDF, "/reports/reporte_ventas_pdf")
    api.add_resource(ReporteVentasExcel, "/reports/reporte_ventas_excel")

if __name__ == "__main__":
    application = create_app()
    port = int(os.environ.get('APP_PORT', 5004))
    application.run(host='0.0.0.0', port=port)