import unittest
import os
from unittest.mock import patch, MagicMock
from flask import json
from app import create_app

class TestReporteVentas(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch("views.report_sales.procesar_reporte")
    def test_reporte_json_exito(self, mock_procesar):
        mock_procesar.return_value = [{"producto": "A", "vendedor": "V1", "unidades_vendidas": 10, "ingresos": 200}]
        response = self.client.get("/reports/reporte_ventas?fecha_inicio=2025-01-01&fecha_fin=2025-04-01")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(response.json), list)
        self.assertEqual(response.json[0]["producto"], "A")

    def test_reporte_json_faltan_fechas(self):
        response = self.client.get("/reports/reporte_ventas")
        self.assertEqual(response.status_code, 400)
        self.assertIn("fecha_inicio", response.json["error"])

    @patch("views.report_sales.procesar_reporte")
    def test_reporte_csv_exito(self, mock_procesar):
        mock_procesar.return_value = [{"producto": "A", "vendedor": "V1", "unidades_vendidas": 10, "ingresos": 200}]
        response = self.client.get("/reports/reporte_ventas_csv?fecha_inicio=2025-01-01&fecha_fin=2025-04-01")

        print("RESPONSE DATA:", response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/csv")

    @patch("views.report_sales.procesar_reporte")
    def test_reporte_csv_sin_datos(self, mock_procesar):
        mock_procesar.return_value = []
        response = self.client.get("/reports/reporte_ventas_csv?fecha_inicio=2025-01-01&fecha_fin=2025-04-01")
        self.assertEqual(response.status_code, 404)
        self.assertIn("No hay datos", response.json["message"])

    @patch("views.report_sales.procesar_reporte")
    def test_reporte_excel_exito(self, mock_procesar):
        mock_procesar.return_value = [{"producto": "A", "vendedor": "V1", "unidades_vendidas": 10, "ingresos": 200}]
        response = self.client.get("/reports/reporte_ventas_excel?fecha_inicio=2025-01-01&fecha_fin=2025-04-01")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # @patch("views.report_sales.procesar_reporte")
    # @patch("pdfkit.from_string")
    # @patch("pdfkit.configuration")
    # def test_reporte_pdf_exito(self, mock_config, mock_pdfkit, mock_procesar):
    #     mock_procesar.return_value = [{"producto": "A", "vendedor": "V1", "unidades_vendidas": 10, "ingresos": 200}]
    #     mock_pdfkit.return_value = b"%PDF-mock"
    #     mock_config.return_value = MagicMock()

    #     response = self.client.get("/reports/reporte_ventas_pdf?fecha_inicio=2025-01-01&fecha_fin=2025-04-01")
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.mimetype, "application/pdf")
