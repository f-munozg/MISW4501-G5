import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from io import BytesIO
import requests
from services.report_logic import procesar_reporte, obtener_ventas, obtener_productos, obtener_vendedores
import os
from flask import json
from requests.exceptions import HTTPError
from app import create_app

from flask_restful import Api
from views.report_sales import (
    ReporteVentas,
    ReporteVentasCSV,
    ReporteVentasExcel,
    # ReporteVentasPDF
)

class TestProcesarReporte(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["TESTING"] = "true"
        cls.app = create_app()
        cls.app.testing = True
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

        # Registrar rutas solo una vez
        if not hasattr(cls.app, 'routes_registered'):
            api = Api(cls.app)
            api.add_resource(ReporteVentas, '/reports/reporte_ventas', endpoint='reporte_ventas_api')
            api.add_resource(ReporteVentasCSV, '/reports/reporte_ventas_csv', endpoint='reporte_ventas_csv_api')
            api.add_resource(ReporteVentasExcel, '/reports/reporte_ventas_excel', endpoint='reporte_ventas_excel_api')
            # api.add_resource(ReporteVentasPDF, '/reports/reporte_ventas_pdf', endpoint='reporte_ventas_pdf_api')
            cls.app.routes_registered = True

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_vendedores")
    def test_ventas_vacias(self, mock_vendedores, mock_productos, mock_ventas):
        mock_ventas.return_value = {"orders": []}
        mock_productos.return_value = {"productos": []}
        mock_vendedores.return_value = {"vendedores": []}

        result = procesar_reporte("2024-01-01", "2024-12-31")
        self.assertEqual(result, [])

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_vendedores")
    def test_orden_sin_seller_id(self, mock_vendedores, mock_productos, mock_ventas):
        mock_ventas.return_value = {
            "orders": [{"date_order": "2024-02-15", "detalle": [{"product_id": 1, "quantity": 2}]}]
        }
        mock_productos.return_value = {"productos": [{"id": 1, "name": "Producto X", "unit_value": 10}]}
        mock_vendedores.return_value = {"vendedores": []}

        result = procesar_reporte("2024-01-01", "2024-12-31")
        self.assertEqual(result[0]["vendedor"], None)
        self.assertEqual(result[0]["producto"], "Producto X")
        self.assertEqual(result[0]["unidades_vendidas"], 2)
        self.assertEqual(result[0]["ingresos"], 20.0)

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_vendedores")
    def test_producto_no_encontrado(self, mock_vendedores, mock_productos, mock_ventas):
        mock_ventas.return_value = {
            "orders": [{"seller_id": 2, "date_order": "2024-03-01", "detalle": [{"product_id": 999, "quantity": 1}]}]
        }
        mock_productos.return_value = {"productos": []}
        mock_vendedores.return_value = {"vendedores": [{"id": 2, "nombre": "Juan"}]}

        result = procesar_reporte("2024-01-01", "2024-12-31")
        self.assertEqual(result[0]["producto"], 999)
        self.assertEqual(result[0]["unidades_vendidas"], 1)
        self.assertEqual(result[0]["ingresos"], 0.0)

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_vendedores")
    def test_vendedor_no_encontrado(self, mock_vendedores, mock_productos, mock_ventas):
        mock_ventas.return_value = {
            "orders": [{"seller_id": 3, "date_order": "2024-03-01", "detalle": [{"product_id": 1, "quantity": 5}]}]
        }
        mock_productos.return_value = {"productos": [{"id": 1, "name": "Producto Z", "unit_value": 20}]}
        mock_vendedores.return_value = {"vendedores": []}

        result = procesar_reporte("2024-01-01", "2024-12-31")
        self.assertEqual(result[0]["vendedor"], 3)
        self.assertEqual(result[0]["ingresos"], 100)

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_vendedores")
    def test_con_filtros_producto_y_vendedor(self, mock_vendedores, mock_productos, mock_ventas):
        mock_ventas.return_value = {
            "orders": [{"seller_id": 1, "date_order": "2024-04-01", "detalle": [{"product_id": 10, "quantity": 3}]}]
        }
        mock_productos.return_value = {"productos": [{"id": 10, "name": "Camisa", "unit_value": 50}]}
        mock_vendedores.return_value = {"vendedores": [{"id": 1, "nombre": "Ana"}]}

        result = procesar_reporte("2024-04-01", "2024-04-30", producto="10", vendedor="1")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["producto"], "Camisa")
        self.assertEqual(result[0]["vendedor"], "Ana")
        self.assertEqual(result[0]["unidades_vendidas"], 3)
        self.assertEqual(result[0]["ingresos"], 150.0)

    @patch("requests.get")
    @patch("requests.post")
    def test_obtener_ventas(self, mock_post, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"orders": [{"seller_id": 1, "date_order": "2024-01-01", "detalle": [{"product_id": 1, "quantity": 2}]}]}
        
        params = {"fecha_inicio": "2024-01-01", "fecha_fin": "2024-01-31"}
        result = obtener_ventas(params)
        self.assertEqual(result, {"orders": [{"seller_id": 1, "date_order": "2024-01-01", "detalle": [{"product_id": 1, "quantity": 2}]}]})

    @patch("requests.get")
    def test_obtener_productos(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"productos": [{"id": 1, "name": "Producto X", "unit_value": 10.0}]}

        params = {"fecha_inicio": "2024-01-01", "fecha_fin": "2024-01-31"}
        result = obtener_productos(params)
        self.assertEqual(result, {"productos": [{"id": 1, "name": "Producto X", "unit_value": 10.0}]})

    @patch("requests.post")
    def test_obtener_vendedores(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"vendedores": [{"id": 1, "nombre": "Vendedor X"}]}

        seller_ids = [1]
        result = obtener_vendedores(seller_ids)
        self.assertEqual(result, {"vendedores": [{"id": 1, "nombre": "Vendedor X"}]})

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_vendedores")
    def test_procesar_reporte(self, mock_obtener_vendedores, mock_obtener_productos, mock_obtener_ventas):
        mock_obtener_ventas.return_value = {"orders": [{"seller_id": 1, "date_order": "2024-01-01", "detalle": [{"product_id": 1, "quantity": 2}]}]}
        mock_obtener_productos.return_value = {"productos": [{"id": 1, "name": "Producto X", "unit_value": 10.0}]}
        mock_obtener_vendedores.return_value = {"vendedores": [{"id": 1, "nombre": "Vendedor X"}]}

        resultado = procesar_reporte("2024-01-01", "2024-01-31")
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["producto"], "Producto X")
        self.assertEqual(resultado[0]["vendedor"], "Vendedor X")
        self.assertEqual(resultado[0]["unidades_vendidas"], 2)
        self.assertEqual(resultado[0]["ingresos"], 20.0)

    @patch("views.report_sales.procesar_reporte")
    def test_reporte_json_api(self, mock_procesar):
        mock_procesar.return_value = [{"producto": "Producto X", "vendedor": "Vendedor X", "unidades_vendidas": 10, "ingresos": 100}]
        response = self.client.get("/reports/reporte_ventas?fecha_inicio=2024-01-01&fecha_fin=2024-04-01")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(response.json), list)

    @patch("views.report_sales.procesar_reporte")
    def test_exportar_csv_api(self, mock_procesar):
        mock_procesar.return_value = [{"producto": "Producto X", "vendedor": "Vendedor X", "unidades_vendidas": 10, "ingresos": 100}]
        response = self.client.get("/reports/reporte_ventas_csv?fecha_inicio=2024-01-01&fecha_fin=2024-04-01")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.decode().startswith("producto,vendedor"))

    @patch("views.report_sales.procesar_reporte")
    def test_exportar_excel_api(self, mock_procesar):
        mock_procesar.return_value = [{"producto": "Producto X", "vendedor": "Vendedor X", "unidades_vendidas": 10, "ingresos": 100}]
        response = self.client.get("/reports/reporte_ventas_excel?fecha_inicio=2024-01-01&fecha_fin=2024-04-01")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.startswith(b"PK"))

    # @patch("views.report_sales.procesar_reporte")
    # @patch("services.report_logic.pdfkit.from_string")
    # @patch("services.report_logic.pdfkit.configuration")
    # def test_exportar_pdf_api(self, mock_config, mock_pdfkit, mock_procesar):
    #     mock_procesar.return_value = [{"producto": "Producto X", "vendedor": "Vendedor X", "unidades_vendidas": 10, "ingresos": 100}]
    #     mock_pdfkit.return_value = b"%PDF-1.4 simulated"
    #     mock_config.return_value = MagicMock()

    #     response = self.client.get("/reports/reporte_ventas_pdf?fecha_inicio=2024-01-01&fecha_fin=2024-04-01")
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTrue(response.data.startswith(b"%PDF"))

    @patch("requests.get")
    def test_obtener_ventas_api_error(self, mock_get):
        mock_get.return_value.status_code = 500
        mock_get.return_value.text = "Error interno del servidor"
        params = {"fecha_inicio": "2024-01-01", "fecha_fin": "2024-01-31"}
        with self.assertRaisesRegex(Exception, "ORDERS API error 500: Error interno del servidor"):
            obtener_ventas(params)

    @patch("requests.get")
    def test_obtener_ventas_invalid_json(self, mock_get):
        mock_response = MagicMock() 
        mock_response.status_code = 200
        mock_response.text = "No es JSON"
        mock_response.json.side_effect = ValueError("No se pudo decodificar JSON")
        mock_get.return_value = mock_response
        params = {"fecha_inicio": "2024-01-01", "fecha_fin": "2024-01-31"}
        with self.assertRaisesRegex(Exception, "Respuesta no es JSON válida desde ORDERS API"):
            obtener_ventas(params)

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_vendedores")
    def test_procesar_reporte_solo_producto(self, mock_vendedores, mock_productos, mock_ventas):
        mock_ventas.return_value = {"orders": [{"seller_id": 1, "date_order": "2024-01-01", "detalle": [{"product_id": 1, "quantity": 2}]}]}
        mock_productos.return_value = {"productos": [{"id": 1, "name": "Producto X", "unit_value": 10.0}]}
        mock_vendedores.return_value = {"vendedores": [{"id": 1, "nombre": "Vendedor X"}]}

        resultado = procesar_reporte("2024-01-01", "2024-01-31", producto="1")
        self.assertEqual(len(resultado), 1)

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_vendedores")
    def test_procesar_reporte_solo_vendedor(self, mock_vendedores, mock_productos, mock_ventas):
        mock_ventas.return_value = {"orders": [{"seller_id": 1, "date_order": "2024-01-01", "detalle": [{"product_id": 1, "quantity": 2}]}]}
        mock_productos.return_value = {"productos": [{"id": 1, "name": "Producto X", "unit_value": 10.0}]}
        mock_vendedores.return_value = {"vendedores": [{"id": 1, "nombre": "Vendedor X"}]}

        resultado = procesar_reporte("2024-01-01", "2024-01-31", vendedor="1")
        self.assertEqual(len(resultado), 1)

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_vendedores")
    def test_procesar_reporte_api_data_incompleta(self, mock_vendedores, mock_productos, mock_ventas):
        mock_ventas.return_value = {"orders": [{"seller_id": 1, "date_order": "2024-01-01", "detalle": [{"product_id": 1, "quantity": 2}]}]}
        mock_productos.return_value = {"productos": [{"id": 1}]}  
        mock_vendedores.return_value = {"vendedores": [{"id": 1}]} 

        resultado = procesar_reporte("2024-01-01", "2024-01-31")
        self.assertEqual(resultado[0]["producto"], 1)
        self.assertEqual(resultado[0]["vendedor"], 1)
        self.assertEqual(resultado[0]["ingresos"], 0.0)

    @patch("requests.get")
    def test_obtener_ventas_connection_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("Error de conexión")
        params = {"fecha_inicio": "2024-01-01", "fecha_fin": "2024-01-31"}
        with self.assertRaisesRegex(Exception, "Error de conexión"):
            obtener_ventas(params)

    @patch("requests.get")
    def test_obtener_productos_connection_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("Error de conexión")
        params = {"fecha_inicio": "2024-01-01", "fecha_fin": "2024-01-31"}
        with self.assertRaises(requests.exceptions.ConnectionError): 
            obtener_productos(params)

    @patch("requests.post")
    def test_obtener_vendedores_timeout(self, mock_post):
        mock_post.side_effect = requests.exceptions.Timeout("Tiempo de espera agotado")
        seller_ids = [1, 2, 3]
        with self.assertRaises(requests.exceptions.Timeout): 
            obtener_vendedores(seller_ids)

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_vendedores")
    def test_procesar_reporte_ventas_none(self, mock_vendedores, mock_productos, mock_ventas):
        mock_ventas.return_value = None 
        mock_productos.return_value = {"productos": []}
        mock_vendedores.return_value = {"vendedores": []}

        resultado = procesar_reporte("2024-01-01", "2024-01-31")
        self.assertEqual(resultado, []) 

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_vendedores")
    def test_procesar_reporte_productos_none(self, mock_vendedores, mock_ventas, mock_productos):
        mock_ventas.return_value = {"orders": []}
        mock_productos.return_value = None 
        mock_vendedores.return_value = {"vendedores": []}

        resultado = procesar_reporte("2024-01-01", "2024-01-31")
        self.assertEqual(resultado, [])

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_vendedores")
    def test_procesar_reporte_vendedores_none(self, mock_productos, mock_ventas, mock_vendedores):
        mock_ventas.return_value = {"orders": []}
        mock_productos.return_value = {"productos": []}
        mock_vendedores.return_value = None

        resultado = procesar_reporte("2024-01-01", "2024-01-31")
        self.assertEqual(resultado, [])

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_vendedores")
    def test_procesar_reporte_orden_seller_id_none(self, mock_vendedores, mock_productos, mock_ventas):
        mock_ventas.return_value = {"orders": [{"seller_id": None, "date_order": "2024-02-15", "detalle": [{"product_id": 1, "quantity": 2}]}]}
        mock_productos.return_value = {"productos": [{"id": 1, "name": "Producto X", "unit_value": 10}]}
        mock_vendedores.return_value = {"vendedores": []}

        resultado = procesar_reporte("2024-01-01", "2024-12-31")
        self.assertIsNone(resultado[0]["vendedor"])

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_vendedores")
    def test_procesar_reporte_orden_detalle_none(self, mock_vendedores, mock_productos, mock_ventas):
        mock_ventas.return_value = {"orders": [{"seller_id": 1, "date_order": "2024-02-15", "detalle": None}]}
        mock_productos.return_value = {"productos": [{"id": 1, "name": "Producto X", "unit_value": 10}]}
        mock_vendedores.return_value = {"vendedores": [{"id": 1, "nombre": "Vendedor 1"}]}

        resultado = procesar_reporte("2024-01-01", "2024-12-31")
        self.assertEqual(resultado, [])

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_vendedores")
    def test_procesar_reporte_item_product_id_none(self, mock_vendedores, mock_productos, mock_ventas):
        mock_ventas.return_value = {"orders": [{"seller_id": 1, "date_order": "2024-02-15", "detalle": [{"product_id": None, "quantity": 2}]}]}
        mock_productos.return_value = {"productos": [{"id": 1, "name": "Producto X", "unit_value": 10}]}
        mock_vendedores.return_value = {"vendedores": [{"id": 1, "nombre": "Vendedor 1"}]}

        resultado = procesar_reporte("2024-01-01", "2024-12-31")
        self.assertEqual(resultado[0]["producto"], None)

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_vendedores")
    def test_procesar_reporte_item_quantity_none(self, mock_vendedores, mock_productos, mock_ventas):
        mock_ventas.return_value = {"orders": [{"seller_id": 1, "date_order": "2024-02-15", "detalle": [{"product_id": 1, "quantity": None}]}]}
        mock_productos.return_value = {"productos": [{"id": 1, "name": "Producto X", "unit_value": 10}]}
        mock_vendedores.return_value = {"vendedores": [{"id": 1, "nombre": "Vendedor 1"}]}

        resultado = procesar_reporte("2024-01-01", "2024-12-31")
        self.assertEqual(resultado[0]["unidades_vendidas"], 0)

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_vendedores")
    def test_procesar_reporte_product_unit_value_none(self, mock_vendedores, mock_productos, mock_ventas):
        mock_ventas.return_value = {"orders": [{"seller_id": 1, "date_order": "2024-02-15", "detalle": [{"product_id": 1, "quantity": 2}]}]}
        mock_productos.return_value = {"productos": [{"id": 1, "name": "Producto X", "unit_value": None}]}
        mock_vendedores.return_value = {"vendedores": [{"id": 1, "nombre": "Vendedor 1"}]}

        resultado = procesar_reporte("2024-01-01", "2024-12-31")
        self.assertEqual(resultado[0]["ingresos"], 0.0)

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_vendedores")
    def test_procesar_reporte_fecha_formato_diferente(self, mock_vendedores, mock_productos, mock_ventas):
        mock_ventas.return_value = {"orders": [{"seller_id": 1, "date_order": "2024/02/15 10:00:00", "detalle": [{"product_id": 1, "quantity": 2}]}]}
        mock_productos.return_value = {"productos": [{"id": 1, "name": "Producto X", "unit_value": 10}]}
        mock_vendedores.return_value = {"vendedores": [{"id": 1, "nombre": "Vendedor 1"}]}

        resultado = procesar_reporte("2024-01-01", "2024-12-31")
        self.assertEqual(resultado[0]["primera_venta"], "2024-02-15")
        self.assertEqual(resultado[0]["ultima_venta"], "2024-02-15")

    @patch("requests.get")
    def test_obtener_ventas_http_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_get.return_value = mock_response
        params = {"fecha_inicio": "2024-01-01", "fecha_fin": "2024-01-31"}
        with self.assertRaisesRegex(Exception, "ORDERS API error 400: Bad Request"):
            obtener_ventas(params)

    @patch("requests.get")
    def test_obtener_ventas_invalid_text(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><h1>Error</h1></body></html>"
        mock_get.return_value = mock_response
        mock_response.json.side_effect = ValueError("Invalid JSON")
        params = {"fecha_inicio": "2024-01-01", "fecha_fin": "2024-01-31"}
        with self.assertRaisesRegex(Exception, "Respuesta no es JSON válida desde ORDERS API"):
            obtener_ventas(params)

    @patch("requests.get")
    def test_obtener_productos_http_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response
        params = {"fecha_inicio": "2024-01-01", "fecha_fin": "2024-01-31"}
        mock_get.side_effect = HTTPError("HTTP Error") 
        with self.assertRaises(HTTPError):
            obtener_productos(params)

    @patch("requests.post")
    def test_obtener_vendedores_http_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_post.return_value = mock_response
        seller_ids = [1, 2, 3]
        mock_post.side_effect = HTTPError("HTTP Error")
        with self.assertRaises(HTTPError):
            obtener_vendedores(seller_ids)

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_vendedores")
    def test_procesar_reporte_api_exception(self, mock_vendedores, mock_productos, mock_ventas):
        mock_ventas.side_effect = Exception("Error al obtener ventas")
        mock_productos.return_value = {"productos": []}
        mock_vendedores.return_value = {"vendedores": []}

        with self.assertRaisesRegex(Exception, "Error al obtener ventas"):
            procesar_reporte("2024-01-01", "2024-01-31")

    @patch("services.report_logic.obtener_ventas")
    @patch("services.report_logic.obtener_productos")
    @patch("services.report_logic.obtener_vendedores")
    def test_procesar_reporte_fechas_limite(self, mock_vendedores, mock_productos, mock_ventas):
        mock_ventas.return_value = {"orders": [{"seller_id": 1, "date_order": "2024-01-01", "detalle": [{"product_id": 1, "quantity": 2}]}]}
        mock_productos.return_value = {"productos": [{"id": 1, "name": "Producto X", "unit_value": 10}]}
        mock_vendedores.return_value = {"vendedores": [{"id": 1, "nombre": "Vendedor 1"}]}

        resultado = procesar_reporte("0001-01-01", "9999-12-31")
        self.assertEqual(len(resultado), 1)