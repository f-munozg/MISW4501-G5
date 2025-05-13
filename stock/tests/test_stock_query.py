import unittest
import os
from unittest.mock import patch, MagicMock
from flask import json
from app import create_app

class TestStockyQuery(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    # @patch("models.models.db.session")
    # def test_stock_query_success(self, mock_db_session):
    #     """Consulta exitosa del stock con filtros válidos."""

    #     mock_query = MagicMock()
    #     mock_query.join.return_value = mock_query
    #     mock_query.filter.return_value = mock_query
    #     mock_query.offset.return_value.limit.return_value.all.return_value = [
    #         MagicMock(
    #             warehouse_name="Bodega Central",
    #             product_name="Arroz",
    #             category=MagicMock(value="ALIMENTACION"),
    #             estimated_delivery_time=None,
    #             date_update=None,
    #             quantity=100
    #         )
    #     ]
    #     mock_query.count.return_value = 1
    #     mock_db_session.query.return_value = mock_query

    #     response = self.client.get(
    #         "/stock/query?product=arroz&category=alimentacion&limit=1&offset=0"
    #     )

    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json["total"], 1)
    #     self.assertEqual(len(response.json["results"]), 1)
    #     self.assertEqual(response.json["results"][0]["product"], "Arroz")

    def test_stock_query_invalid_limit_offset(self):
        """Debe fallar cuando limit u offset no son enteros."""
        response = self.client.get("/stock/query?limit=abc&offset=xyz")
        self.assertEqual(response.status_code, 400)
        self.assertIn("limit and offset must be integers", response.json["message"])

    def test_stock_query_invalid_category(self):
        """Debe fallar cuando la categoría no existe en el enum."""
        response = self.client.get("/stock/query?category=invalida")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid category", response.json["message"])

    @patch("models.models.db.session")
    def test_stock_query_no_filters(self, mock_db_session):
        """Consulta sin filtros aplicados."""
        mock_query = MagicMock()
        mock_query.join.return_value = mock_query
        mock_query.offset.return_value.limit.return_value.all.return_value = []
        mock_query.count.return_value = 0
        mock_db_session.query.return_value = mock_query

        response = self.client.get("/stock/query")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["total"], 0)
        self.assertEqual(response.json["results"], [])