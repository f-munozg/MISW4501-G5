import unittest
import os
from unittest.mock import patch, MagicMock
from flask import json
from app import create_app
from flask_restful import Api
from views.report_seller import ReporteVendedor, ReporteVendedorCSV, ReporteVendedorExcel
import uuid

class TestReporteVendedor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["TESTING"] = "true"
        cls.app = create_app()
        cls.app.testing = True
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

        # Registrar rutas solo una vez para toda la clase de pruebas
        api = Api(cls.app)
        api.add_resource(ReporteVendedor, '/reports/reporte_vendedor', endpoint='reporte_vendedor_test')
        api.add_resource(ReporteVendedorCSV, '/reports/reporte_vendedor_csv', endpoint='reporte_vendedor_csv_test')
        api.add_resource(ReporteVendedorExcel, '/reports/reporte_vendedor_excel', endpoint='reporte_vendedor_excel_test')

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()

    def setUp(self):
        # Crear un UUID válido para las pruebas
        self.valid_uuid = str(uuid.uuid4())

    def tearDown(self):
        pass

    @patch("views.report_seller.procesar_reporte_vendedor")
    def test_reporte_vendedor_json_exito(self, mock_procesar):
        mock_procesar.return_value = {
            "resumen": {
                "total_ventas": 1000,
                "clientes_atendidos": 5,
                "clientes_visitados": 10,
                "tasa_conversion": 50,
                "plan": {
                    "periodo": "TRIMESTRAL",
                    "meta": 2000,
                    "cumplimiento": "50.0%"
                }
            },
            "detalle_productos": [
                {
                    "producto": "Producto 1",
                    "cantidad": 10,
                    "valor_unitario": 100,
                    "valor_total": 1000
                }
            ]
        }
        response = self.client.get(f"/reports/reporte_vendedor?fecha_inicio=2024-01-01&fecha_fin=2024-04-01&seller_id={self.valid_uuid}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(response.json), dict)
        self.assertIn("resumen", response.json)
        self.assertIn("detalle_productos", response.json)

    def test_reporte_vendedor_json_faltan_parametros(self):
        response = self.client.get("/reports/reporte_vendedor")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)

    def test_reporte_vendedor_json_falta_seller_id(self):
        response = self.client.get("/reports/reporte_vendedor?fecha_inicio=2024-01-01&fecha_fin=2024-04-01")
        self.assertEqual(response.status_code, 400)
        self.assertIn("seller_id es requerido", response.json["error"])

    @patch("views.report_seller.procesar_reporte_vendedor")
    def test_reporte_vendedor_csv_exito(self, mock_procesar):
        mock_procesar.return_value = {
            "resumen": {
                "total_ventas": 1000,
                "clientes_atendidos": 5,
                "tasa_conversion": 50
            },
            "detalle_productos": [
                {
                    "producto": "Producto 1",
                    "fecha_venta": "2024-01-15",
                    "cantidad": 10,
                    "valor_unitario": 100,
                    "valor_total": 1000
                }
            ]
        }
        response = self.client.get(f"/reports/reporte_vendedor_csv?fecha_inicio=2024-01-01&fecha_fin=2024-04-01&seller_id={self.valid_uuid}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/csv")

    @patch("views.report_seller.procesar_reporte_vendedor")
    def test_reporte_vendedor_excel_exito(self, mock_procesar):
        mock_procesar.return_value = {
            "resumen": {
                "total_ventas": 1000,
                "total_ventas_plan": 800,
                "clientes_atendidos": 5,
                "clientes_visitados": 10,
                "tasa_conversion": 50,
                "plan": {
                    "periodo": "TRIMESTRAL",
                    "meta": 2000,
                    "cumplimiento": "50.0%"
                }
            },
            "detalle_productos": [
                {
                    "producto": "Producto 1",
                    "fecha_venta": "2024-01-15",
                    "cantidad": 10,
                    "valor_unitario": 100,
                    "valor_total": 1000
                }
            ]
        }
        response = self.client.get(f"/reports/reporte_vendedor_excel?fecha_inicio=2024-01-01&fecha_fin=2024-04-01&seller_id={self.valid_uuid}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    @patch("views.report_seller.procesar_reporte_vendedor")
    def test_reporte_vendedor_sin_datos(self, mock_procesar):
        mock_procesar.return_value = {
            "resumen": {
                "total_ventas": 0,
                "clientes_atendidos": 0,
                "clientes_visitados": 0,
                "tasa_conversion": 0,
                "plan": {
                    "periodo": "No tiene plan activo",
                    "meta": 0,
                    "cumplimiento": "0.0%"
                }
            },
            "detalle_productos": []
        }
        response = self.client.get(f"/reports/reporte_vendedor?fecha_inicio=2024-01-01&fecha_fin=2024-04-01&seller_id={self.valid_uuid}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["resumen"]["total_ventas"], 0)
        self.assertEqual(len(response.json["detalle_productos"]), 0)

    @patch("views.report_seller.procesar_reporte_vendedor")
    def test_reporte_vendedor_error_interno(self, mock_procesar):
        mock_procesar.side_effect = Exception("Error interno del servidor")
        response = self.client.get(f"/reports/reporte_vendedor?fecha_inicio=2024-01-01&fecha_fin=2024-04-01&seller_id={self.valid_uuid}")
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)

    @patch("views.report_seller.procesar_reporte_vendedor")
    def test_reporte_vendedor_fechas_invalidas(self, mock_procesar):
        response = self.client.get(f"/reports/reporte_vendedor?fecha_inicio=fecha-invalida&fecha_fin=2024-04-01&seller_id={self.valid_uuid}")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)

    @patch("views.report_seller.procesar_reporte_vendedor")
    def test_reporte_vendedor_seller_id_invalido(self, mock_procesar):
        response = self.client.get("/reports/reporte_vendedor?fecha_inicio=2024-01-01&fecha_fin=2024-04-01&seller_id=invalid-uuid")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json) 