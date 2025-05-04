import unittest
from unittest.mock import patch, MagicMock
from flask import json
from app import create_app
from sqlalchemy.exc import SQLAlchemyError
from uuid import uuid4


class TestStockCriticalCheck(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch("models.models.db.session")
    def test_no_critical_stock_found(self, mock_db_session):
        mock_db_session.query.return_value.options.return_value.filter.return_value.all.return_value = []

        response = self.client.post("/stock/critical")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "No critical stock found")

    @patch("models.models.db.session")
    def test_critical_stock_detected(self, mock_db_session):
        mock_stock = MagicMock()
        mock_stock.product_id = uuid4()
        mock_stock.product.name = "Aspirina"
        mock_stock.warehouse.name = "Central"
        mock_stock.quantity = 5
        mock_stock.threshold_stock = 10
        mock_stock.warehouse_id = uuid4()

        type(mock_stock).critical_level = False

        mock_db_session.query.return_value.options.return_value.filter.return_value.all.return_value = [mock_stock]

        mock_db_session.query.return_value.filter.return_value.all.side_effect = [[], []]

        response = self.client.post("/stock/critical")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Critical stock detected")
        self.assertTrue("critical_products" in response.json)
        self.assertEqual(len(response.json["critical_products"]), 1)
        self.assertEqual(response.json["critical_products"][0]["product_name"], "Aspirina")

    @patch("models.models.db.session")
    def test_database_error(self, mock_db_session):
        mock_db_session.query.side_effect = SQLAlchemyError("DB error")

        response = self.client.post("/stock/critical")

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json["message"], "Database error")
        self.assertIn("details", response.json)

    @patch("models.models.db.session")
    def test_unexpected_error(self, mock_db_session):
        mock_db_session.query.side_effect = Exception("Unexpected")

        response = self.client.post("/stock/critical")

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json["message"], "Unexpected error")
        self.assertIn("details", response.json)