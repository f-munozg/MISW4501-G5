import unittest
import os
from unittest.mock import patch, MagicMock
from flask import json
from app import create_app

class TestProductStockLocation(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_missing_filters(self):
        """Debe fallar si no se envía ni 'product' ni 'warehouse_id'."""
        response = self.client.get("/stock/product_location")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Debe enviar al menos", response.json["error"])

    def test_invalid_limit_offset(self):
        """Debe fallar si limit u offset no son números."""
        response = self.client.get("/stock/product_location?product=SKU-123&limit=abc&offset=xyz")
        self.assertEqual(response.status_code, 400)
        self.assertIn("limit and offset must be integers", response.json["message"])

    @patch("models.models.db.session")
    def test_valid_search_filter(self, mock_db_session):
        """Debe ejecutar correctamente si solo se envía 'product'."""
        mock_query = MagicMock()
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.offset.return_value.limit.return_value.all.return_value = []
        mock_query.count.return_value = 0
        mock_db_session.query.return_value = mock_query

        response = self.client.get("/stock/product_location?product=ABC")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["total"], 0)
        self.assertEqual(response.json["results"], [])

    @patch("models.models.db.session")
    def test_valid_warehouse_filter(self, mock_db_session):
        """Debe ejecutar correctamente si solo se envía 'warehouse_id'."""
        mock_query = MagicMock()
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.offset.return_value.limit.return_value.all.return_value = []
        mock_query.count.return_value = 0
        mock_db_session.query.return_value = mock_query

        response = self.client.get("/stock/product_location?warehouse_id=some-id")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["total"], 0)
        self.assertEqual(response.json["results"], [])

    @patch("models.models.db.session")
    def test_valid_both_filters_with_results(self, mock_db_session):
        """Debe devolver productos si vienen ambos filtros y hay datos."""
        # Simular resultado de la query
        mock_row = MagicMock()
        mock_row.product_name = "Producto X"
        mock_row.sku = "SKU-123"
        mock_row.quantity = 50
        mock_row.location = "Pasillo A"
        mock_row.expiration_date = None

        mock_query = MagicMock()
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.offset.return_value.limit.return_value.all.return_value = [mock_row]
        mock_query.count.return_value = 1
        mock_db_session.query.return_value = mock_query

        response = self.client.get("/stock/product_location?product=SKU-123&warehouse_id=abc123")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["total"], 1)
        self.assertEqual(len(response.json["results"]), 1)
        self.assertEqual(response.json["results"][0]["status"], "Vigente")