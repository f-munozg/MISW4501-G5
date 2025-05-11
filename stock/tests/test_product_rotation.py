import unittest
import os
from unittest.mock import patch, MagicMock
from app import create_app
from datetime import datetime
from models.models import StockMovementType
import uuid
import json

class TestProductRotationReport(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.product_id = str(uuid.uuid4())
        self.start_date = "2024-01-01"
        self.end_date = "2024-01-31"
        
        self.mock_product = MagicMock(
            id=uuid.UUID(self.product_id),
            sku="TEST123",
            name="Producto de prueba"
        )
        self.mock_product.id = uuid.UUID(self.product_id)
        self.mock_product.sku = "TEST123"
        self.mock_product.name = "Producto de prueba"

    def tearDown(self):
        self.app_context.pop()

    def create_mock_history_log(self, timestamp, quantity, movement_type, alert_message=None):
        mock = MagicMock()
        mock.product_id = uuid.UUID(self.product_id)
        mock.timestamp = timestamp
        mock.quantity = quantity
        mock.movement_type = movement_type
        mock.alert_message = alert_message
        return mock

    @patch("models.models.db.session.query")
    def test_successful_report(self, mock_query):
        mock_product_query = MagicMock()
        mock_product_query.filter_by.return_value.first.return_value = self.mock_product
        
        ingresos = self.create_mock_history_log(
            timestamp=datetime(2024, 1, 10),
            quantity=100,
            movement_type=StockMovementType.INGRESO,
            alert_message=None
        )
        
        salidas = self.create_mock_history_log(
            timestamp=datetime(2024, 1, 15),
            quantity=30,
            movement_type=StockMovementType.SALIDA,
            alert_message=None
        )
        
        mock_history_query = MagicMock()
        mock_history_query.filter.return_value.order_by.return_value.all.return_value = [ingresos, salidas]
        
        mock_query.side_effect = [mock_product_query, mock_history_query]

        response = self.client.get(
            f"/stock/product_rotation?product_id={self.product_id}&start_date={self.start_date}&end_date={self.end_date}"
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(data["product_id"], self.product_id)
        self.assertEqual(data["sku"], "TEST123")
        self.assertEqual(data["name"], "Producto de prueba")
        self.assertEqual(data["stock_inicial"], 100)
        self.assertEqual(data["stock_final"], 70)
        self.assertEqual(data["rotacion"]["porcentaje"], 30.0)
        self.assertEqual(len(data["movimientos"]), 2)

    @patch("models.models.db.session.query")
    def test_report_with_default_dates(self, mock_query):
        mock_product_query = MagicMock()
        mock_product_query.filter_by.return_value.first.return_value = self.mock_product
        
        mock_history_query = MagicMock()
        mock_history_query.filter.return_value.order_by.return_value.all.return_value = []
        
        mock_query.side_effect = [mock_product_query, mock_history_query]

        response = self.client.get(
            f"/stock/product_rotation?product_id={self.product_id}"
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["product_id"], self.product_id)
        self.assertEqual(len(data["movimientos"]), 0)

    def test_invalid_product_id(self):
        response = self.client.get("/stock/product_rotation?product_id=invalid_id")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data), {"message": "Invalid or missing product_id"})

    @patch("models.models.db.session.query")
    def test_product_not_found(self, mock_query):
        mock_product_query = MagicMock()
        mock_product_query.filter_by.return_value.first.return_value = None
        mock_query.return_value = mock_product_query

        response = self.client.get(f"/stock/product_rotation?product_id={self.product_id}")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.data), {"message": "Product not found"})

    def test_invalid_date_format(self):
        response = self.client.get(f"/stock/product_rotation?product_id={self.product_id}&start_date=2024/01/01")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data), {"message": "Invalid date format. Use YYYY-MM-DD"})

    @patch("models.models.db.session.query")
    def test_rotation_levels(self, mock_query):
        # Configurar mocks para probar diferentes niveles de rotación
        test_cases = [
            (100, 90, "Alta"),    # 90% rotación
            (100, 60, "Media"),    # 60% rotación
            (100, 20, "Baja"),      # 20% rotación
            (0, 0, "Baja")          # 0% rotación (caso borde)
        ]

        for stock_inicial, stock_consumido, expected_level in test_cases:
            with self.subTest(stock_inicial=stock_inicial, stock_consumido=stock_consumido):
                mock_product_query = MagicMock()
                mock_product_query.filter_by.return_value.first.return_value = self.mock_product
                
                # Crear movimientos según el caso de prueba
                movimientos = []
                if stock_inicial > 0:
                    movimientos.append(self.create_mock_history_log(
                        timestamp=datetime(2024, 1, 1),
                        quantity=stock_inicial,
                        movement_type=StockMovementType.INGRESO,
                        alert_message=None
                    ))
                    movimientos.append(self.create_mock_history_log(
                        timestamp=datetime(2024, 1, 2),
                        quantity=stock_consumido,
                        movement_type=StockMovementType.SALIDA,
                        alert_message=None
                    ))
                
                mock_history_query = MagicMock()
                mock_history_query.filter.return_value.order_by.return_value.all.return_value = movimientos
                
                mock_query.side_effect = [mock_product_query, mock_history_query]

                response = self.client.get(
                    f"/stock/product_rotation?product_id={self.product_id}&start_date={self.start_date}&end_date={self.end_date}"
                )

                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertEqual(data["rotacion"]["nivel"], expected_level)

    @patch("models.models.db.session.query")
    def test_filter_alert_messages(self, mock_query):
        mock_product_query = MagicMock()
        mock_product_query.filter_by.return_value.first.return_value = self.mock_product
        
        valid_movement = self.create_mock_history_log(
            timestamp=datetime(2024, 1, 15),
            quantity=30,
            movement_type=StockMovementType.SALIDA,
            alert_message=None
        )
        
        mock_history_query = MagicMock()
        mock_history_query.filter.return_value.order_by.return_value.all.return_value = [valid_movement]
        
        mock_query.side_effect = [mock_product_query, mock_history_query]

        response = self.client.get(f"/stock/product_rotation?product_id={self.product_id}&start_date={self.start_date}&end_date={self.end_date}")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data["movimientos"]), 1)
        self.assertEqual(data["movimientos"][0]["cantidad_salida"], 30)