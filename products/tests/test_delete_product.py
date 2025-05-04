import unittest
import os
from unittest.mock import patch, MagicMock
from uuid import uuid4
from app import create_app

class DeleteProductTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        self.product_id = str(uuid4())
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch("views.delete_product.db")
    def test_delete_product_success(self, mock_db):
        mock_product = MagicMock()
        mock_query = mock_db.session.query.return_value
        mock_filter = mock_query.filter_by.return_value
        mock_filter.first.return_value = mock_product

        response = self.client.delete(f"/products/{self.product_id}")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Product deleted successfully", response.get_json()["message"])
        mock_db.session.delete.assert_called_once_with(mock_product)
        mock_db.session.commit.assert_called_once()

    @patch("views.delete_product.db")
    def test_delete_product_invalid_id(self, mock_db):
        response = self.client.delete("/products/invalid-uuid")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid product ID", response.get_json()["message"])

    @patch("views.delete_product.db")
    def test_delete_product_not_found(self, mock_db):
        mock_query = mock_db.session.query.return_value
        mock_filter = mock_query.filter_by.return_value
        mock_filter.first.return_value = None

        response = self.client.delete(f"/products/{self.product_id}")

        self.assertEqual(response.status_code, 404)
        self.assertIn("Product not found", response.get_json()["message"])
