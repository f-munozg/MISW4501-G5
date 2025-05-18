import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from io import BytesIO
import requests
from services.report_logic import procesar_reporte_vendedor
import os
from flask import json
from requests.exceptions import HTTPError
from app import create_app

class TestProcesarReporteVendedor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["TESTING"] = "true"
        cls.app = create_app()
        cls.app.testing = True
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_metas_vendedor")
    @patch("services.report_logic.obtener_rutas_vendedor")
    def test_reporte_vendedor_sin_datos(self, mock_rutas, mock_metas, mock_productos, mock_ventas):
        mock_ventas.return_value = {"orders": []}
        mock_productos.return_value = {"productos": []}
        mock_metas.return_value = None
        mock_rutas.return_value = {"routes": []}

        resultado = procesar_reporte_vendedor("2024-01-01", "2024-12-31", "1")
        self.assertEqual(resultado["resumen"]["total_ventas"], 0)
        self.assertEqual(resultado["resumen"]["clientes_atendidos"], 0)

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_metas_vendedor")
    @patch("services.report_logic.obtener_rutas_vendedor")
    def test_reporte_vendedor_con_ventas(self, mock_rutas, mock_metas, mock_productos, mock_ventas):
        mock_ventas.return_value = {
            "orders": [{
                "seller_id": "1",
                "date_order": "2024-01-15",
                "customer_id": "C1",
                "detalle": [{"product_id": "P1", "quantity": 5}]
            }]
        }
        mock_productos.return_value = {
            "productos": [{"id": "P1", "name": "Producto 1", "unit_value": 100}]
        }
        mock_metas.return_value = {
            "target": 1000,
            "product_id": "P1",
            "period": "TRIMESTRAL"
        }
        mock_rutas.return_value = {
            "routes": [{
                "stops": [{"customer_id": "C1"}, {"customer_id": "C2"}]
            }]
        }

        resultado = procesar_reporte_vendedor("2024-01-01", "2024-12-31", "1")
        self.assertEqual(resultado["resumen"]["total_ventas"], 500)
        self.assertEqual(resultado["resumen"]["clientes_atendidos"], 1)
        self.assertEqual(resultado["resumen"]["clientes_visitados"], 2)
        self.assertEqual(len(resultado["detalle_productos"]), 1)

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_metas_vendedor")
    @patch("services.report_logic.obtener_rutas_vendedor")
    def test_reporte_vendedor_calculo_tasa_conversion(self, mock_rutas, mock_metas, mock_productos, mock_ventas):
        mock_ventas.return_value = {
            "orders": [{
                "seller_id": "1",
                "customer_id": "C1",
                "date_order": "2024-01-15",
                "detalle": [{"product_id": "P1", "quantity": 1}]
            }]
        }
        mock_productos.return_value = {
            "productos": [{"id": "P1", "name": "Producto 1", "unit_value": 100}]
        }
        mock_metas.return_value = None
        mock_rutas.return_value = {
            "routes": [{
                "stops": [{"customer_id": "C1"}, {"customer_id": "C2"}]
            }]
        }

        resultado = procesar_reporte_vendedor("2024-01-01", "2024-12-31", "1")
        self.assertEqual(resultado["resumen"]["tasa_conversion"], 50)

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_metas_vendedor")
    @patch("services.report_logic.obtener_rutas_vendedor")
    def test_reporte_vendedor_cumplimiento_meta(self, mock_rutas, mock_metas, mock_productos, mock_ventas):
        mock_ventas.return_value = {
            "orders": [{
                "seller_id": "1",
                "date_order": "2024-01-15",
                "detalle": [{"product_id": "P1", "quantity": 10}]
            }]
        }
        mock_productos.return_value = {
            "productos": [{"id": "P1", "name": "Producto 1", "unit_value": 100}]
        }
        mock_metas.return_value = {
            "target": 500,
            "product_id": "P1",
            "period": "TRIMESTRAL"
        }
        mock_rutas.return_value = {"routes": []}

        resultado = procesar_reporte_vendedor("2024-01-01", "2024-12-31", "1")
        self.assertEqual(resultado["resumen"]["plan"]["cumplimiento"], "200.0%")

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_metas_vendedor")
    @patch("services.report_logic.obtener_rutas_vendedor")
    def test_reporte_vendedor_sin_metas(self, mock_rutas, mock_metas, mock_productos, mock_ventas):
        mock_ventas.return_value = {
            "orders": [{
                "seller_id": "1",
                "date_order": "2024-01-15",
                "detalle": [{"product_id": "P1", "quantity": 1}]
            }]
        }
        mock_productos.return_value = {
            "productos": [{"id": "P1", "name": "Producto 1", "unit_value": 100}]
        }
        mock_metas.return_value = None
        mock_rutas.return_value = {"routes": []}

        resultado = procesar_reporte_vendedor("2024-01-01", "2024-12-31", "1")
        self.assertEqual(resultado["resumen"]["plan"]["periodo"], "No tiene plan activo")
        self.assertEqual(resultado["resumen"]["plan"]["meta"], 0)

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_metas_vendedor")
    @patch("services.report_logic.obtener_rutas_vendedor")
    def test_reporte_vendedor_error_api(self, mock_rutas, mock_metas, mock_productos, mock_ventas):
        mock_ventas.side_effect = Exception("Error en API de ventas")
        mock_productos.return_value = {"productos": []}
        mock_metas.return_value = None
        mock_rutas.return_value = {"routes": []}

        resultado = procesar_reporte_vendedor("2024-01-01", "2024-12-31", "1")
        self.assertEqual(resultado["resumen"]["total_ventas"], 0)
        self.assertEqual(resultado["resumen"]["clientes_atendidos"], 0)
        self.assertEqual(len(resultado["detalle_productos"]), 0)

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_metas_vendedor")
    @patch("services.report_logic.obtener_rutas_vendedor")
    def test_reporte_vendedor_multiples_productos(self, mock_rutas, mock_metas, mock_productos, mock_ventas):
        mock_ventas.return_value = {
            "orders": [{
                "seller_id": "1",
                "date_order": "2024-01-15",
                "detalle": [
                    {"product_id": "P1", "quantity": 2},
                    {"product_id": "P2", "quantity": 3}
                ]
            }]
        }
        mock_productos.return_value = {
            "productos": [
                {"id": "P1", "name": "Producto 1", "unit_value": 100},
                {"id": "P2", "name": "Producto 2", "unit_value": 150}
            ]
        }
        mock_metas.return_value = None
        mock_rutas.return_value = {"routes": []}

        resultado = procesar_reporte_vendedor("2024-01-01", "2024-12-31", "1")
        self.assertEqual(len(resultado["detalle_productos"]), 2)
        self.assertEqual(resultado["resumen"]["total_ventas"], 650)

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_metas_vendedor")
    @patch("services.report_logic.obtener_rutas_vendedor")
    def test_reporte_vendedor_sin_seller_id(self, mock_rutas, mock_metas, mock_productos, mock_ventas):
        resultado, codigo = procesar_reporte_vendedor("2024-01-01", "2024-12-31", None)
        self.assertEqual(codigo, 400)
        self.assertEqual(resultado["message"], "El ID del vendedor es requerido")

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_metas_vendedor")
    @patch("services.report_logic.obtener_rutas_vendedor")
    def test_reporte_vendedor_datos_invalidos(self, mock_rutas, mock_metas, mock_productos, mock_ventas):
        mock_ventas.return_value = {
            "orders": [{
                "seller_id": "1",
                "date_order": "fecha_invalida",
                "detalle": [{"product_id": "P1", "quantity": "no_numerico"}]
            }]
        }
        mock_productos.return_value = {
            "productos": [{"id": "P1", "name": "Producto 1", "unit_value": "no_numerico"}]
        }
        mock_metas.return_value = None
        mock_rutas.return_value = {"routes": []}

        resultado = procesar_reporte_vendedor("2024-01-01", "2024-12-31", "1")
        self.assertEqual(resultado["resumen"]["total_ventas"], 0)
        self.assertEqual(len(resultado["detalle_productos"]), 0)

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_metas_vendedor")
    @patch("services.report_logic.obtener_rutas_vendedor")
    def test_reporte_vendedor_error_conexion(self, mock_rutas, mock_metas, mock_productos, mock_ventas):
        mock_ventas.side_effect = requests.exceptions.ConnectionError("Error de conexión")
        mock_productos.return_value = {"productos": []}
        mock_metas.return_value = None
        mock_rutas.return_value = {"routes": []}

        resultado = procesar_reporte_vendedor("2024-01-01", "2024-12-31", "1")
        self.assertEqual(resultado["resumen"]["total_ventas"], 0)
        self.assertEqual(resultado["resumen"]["clientes_atendidos"], 0)
        self.assertEqual(len(resultado["detalle_productos"]), 0) 