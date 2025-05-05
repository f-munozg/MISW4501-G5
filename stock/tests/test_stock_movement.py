import unittest
import os
from unittest.mock import patch, MagicMock
from app import create_app
from datetime import datetime
import uuid
from flask import json
from views.stock_movements import StockMovement

class TestStockMovement(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch("models.models.db.session")
    def test_inventory_entry_success(self, mock_session):
        mock_add = MagicMock()
        mock_commit = MagicMock()
        mock_query = MagicMock()
        mock_stock = MagicMock()
        mock_stock.quantity = 10
        mock_stock.threshold_stock = 0
        mock_query.return_value.filter_by.return_value.first.return_value = mock_stock

        mock_session.query.return_value = mock_query.return_value
        mock_session.add = mock_add
        mock_session.commit = mock_commit

        payload = {
            "product_id": str(uuid.uuid4()),
            "warehouse_id": str(uuid.uuid4()),
            "quantity": 5,
            "movement_type": "ingreso",
            "user": "admin",
            "destination": "Main store"
        }

        response = self.client.post("/stock/movement", json=payload)

        self.assertEqual(response.status_code, 201)
        self.assertIn("Stock movement processed successfully", response.get_json()["message"])

    @patch("models.models.db.session")
    def test_inventory_exit_with_insufficient_stock(self, mock_session):
        mock_add = MagicMock()
        mock_commit = MagicMock()
        mock_query = MagicMock()
        mock_stock = MagicMock()
        mock_stock.quantity = 2
        mock_query.return_value.filter_by.return_value.first.return_value = mock_stock

        mock_session.query.return_value = mock_query.return_value
        mock_session.add = mock_add
        mock_session.commit = mock_commit

        payload = {
            "product_id": str(uuid.uuid4()),
            "warehouse_id": str(uuid.uuid4()),
            "quantity": 5,
            "movement_type": "salida",
            "user": "admin",
            "destination": "Sucursal 2"
        }

        response = self.client.post("/stock/movement", json=payload)

        self.assertEqual(response.status_code, 409)
        self.assertIn("Insufficient stock", response.get_json()["message"])

    def test_missing_required_fields(self):
        payload = {
            "product_id": str(uuid.uuid4()),
            "quantity": 5,
            "movement_type": "ingreso",
            "user": "admin"
        }
        response = self.client.post("/stock/movement", json=payload)

        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required fields", response.get_json()["message"])

    def test_invalid_movement_type(self):
        payload = {
            "product_id": str(uuid.uuid4()),
            "warehouse_id": str(uuid.uuid4()),
            "quantity": 5,
            "movement_type": "registro",
            "user": "admin",
            "destination": "Sucursal 3"
        }

        response = self.client.post("/stock/movement", json=payload)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["message"], "Invalid movement_type. Must be 'INGRESO' or 'SALIDA'")

    @patch("views.stock_movements.requests.request")
    @patch("views.stock_movements.db.session")
    def test_get_stock_movements_success(self, mock_db_session, mock_requests):
        # Mock de movimientos
        log = MagicMock()
        log.timestamp = datetime(2025, 5, 3, 17, 0)
        log.product.name = "Ibuprofeno"
        log.warehouse.name = "Bodega Central"
        log.movement_type.value = "INGRESO"
        log.quantity = 10
        log.user = "user-id-123"

        mock_db_session.query.return_value.options.return_value.order_by.return_value.all.return_value = [log]

        # Mock de llamada a users service
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "users": [{"id": "user-id-123", "username": "Carlos Ruiz"}]
        }
        mock_requests.return_value = mock_response

        response = self.client.get("/stock/movement")
        self.assertEqual(response.status_code, 200)
        self.assertIn("movimientos", response.json)
        self.assertEqual(len(response.json["movimientos"]), 1)
        self.assertEqual(response.json["movimientos"][0]["usuario"], "Carlos Ruiz")

    @patch("views.stock_movements.requests.request")
    @patch("views.stock_movements.db.session")
    def test_get_stock_movements_user_service_error(self, mock_db_session, mock_requests):
        # Simula logs válidos
        log = MagicMock()
        log.timestamp = datetime.utcnow()
        log.product.name = "Aspirina"
        log.warehouse.name = "Bodega Norte"
        log.movement_type.value = "SALIDA"
        log.quantity = 5
        log.user = "user-id-456"

        mock_db_session.query.return_value.options.return_value.order_by.return_value.all.return_value = [log]

        # Simula error al llamar al servicio de usuarios
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "error"}
        mock_requests.return_value = mock_response

        response = self.client.get("/stock/movement")
        self.assertEqual(response.status_code, 500)
        self.assertIn("message", response.json)

    @patch("views.stock_movements.requests.request", side_effect=Exception("fallo inesperado"))
    def test_get_stock_movements_exception(self, mock_requests):
        response = self.client.get("/stock/movement")
        self.assertEqual(response.status_code, 500)
        self.assertIn("Error al consultar movimientos de stock", response.json["message"])