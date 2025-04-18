import unittest
import os
from unittest.mock import patch, MagicMock
from app import create_app
from datetime import datetime
import uuid

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

