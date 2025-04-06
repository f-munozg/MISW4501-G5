import unittest
import os
from unittest.mock import patch, MagicMock
from app import create_app
from datetime import datetime
from models.models import ProductCategory
import uuid


class TestProductsWithStock(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch("models.models.db.session.query")
    def test_with_data(self, mock_query):
        # Setup de mocks
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance

        # Mocks para count y all
        mock_query_instance.join.return_value.filter.return_value.count.return_value = 1
        mock_query_instance.join.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = [
            MagicMock(
                product_name="Producto 1",
                sku="SKU123",
                photo="foto.jpg",
                category=ProductCategory.FARMACIA,
                estimated_delivery_time=datetime(2024, 4, 2, 12, 0, 0),
                quantity=5,
                date_update=datetime(2024, 4, 1, 15, 0, 0),
                unit_value=10.000
            )
        ]

        response = self.client.get("/stock/get")

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["results"][0]["product"], "Producto 1")

    def test_invalid_offset_and_limit(self):
        response = self.client.get("/stock/get?limit=abc&offset=xyz")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"message": "limit and offset must be integers"})

    @patch("models.models.db.session.query")
    def test_with_pagination(self, mock_query):
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance

        mock_query_instance.join.return_value.filter.return_value.count.return_value = 3
        mock_query_instance.join.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = [
            MagicMock(
                product_name="Producto 2",
                sku="SKU456",
                photo=None,
                category=ProductCategory.ELECTRÓNICA,
                estimated_delivery_time=None,
                quantity=10,
                date_update=None,
                unit_value=10.000
            )
        ]

        response = self.client.get("/stock/get?limit=1&offset=1")

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["limit"], 1)
        self.assertEqual(data["offset"], 1)
        self.assertEqual(data["total"], 3)
        self.assertEqual(data["results"][0]["sku"], "SKU456")


if __name__ == '__main__':
    unittest.main()
