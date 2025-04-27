import unittest
import os
from unittest.mock import patch, MagicMock
from flask import json
from app import create_app
from sqlalchemy.exc import IntegrityError

class TestAddSalesPlan(unittest.TestCase):
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
    def test_create_sales_plan_success(self, mock_db_session):
        """Prueba la creación exitosa de un plan de ventas."""
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()

        payload = {
            "seller_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
            "target": 10000,
            "product_id": "1c3e3f36-cd99-4d60-8594-9cc971a928e5",
            "period": "TRIMESTRAL"
        }

        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = None
        mock_db_session.query.return_value = mock_query

        response = self.client.post(
            "/sales-plans/add",
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["message"], "Sales period created successfully")
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @patch("models.models.db.session")
    def test_create_sales_plan_missing_fields(self, mock_db_session):
        """Prueba que falla si faltan campos obligatorios."""
        payload = {
            "seller_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
            "target": 10000,
        }

        response = self.client.post(
            "/sales-plans/add",
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required fields", response.json["message"])
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()

    @patch("models.models.db.session")
    def test_create_sales_plan_integrity_error(self, mock_db_session):
        """Prueba que ya existe un plan activo duplicado para el mismo vendedor y periodo."""
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()

        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = MagicMock()
        mock_db_session.query.return_value = mock_query

        payload = {
            "seller_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
            "target": 10000,
            "product_id": "1c3e3f36-cd99-4d60-8594-9cc971a928e5",
            "period": "TRIMESTRAL" 
        }

        response = self.client.post(
            "/sales-plans/add",
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 409)
        self.assertIn("already exists", response.json["message"])
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()

    @patch("models.models.db.session")
    def test_create_sales_plan_duplicate_active(self, mock_db_session):
        """Prueba que no se pueda crear un plan activo duplicado para mismo vendedor y periodo."""
        
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = MagicMock()
        mock_db_session.query.return_value = mock_query

        payload = {
            "seller_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
            "target": 10000,
            "product_id": "1c3e3f36-cd99-4d60-8594-9cc971a928e5",
            "period": "TRIMESTRAL"
        }

        response = self.client.post(
            "/sales-plans/add",
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 409)
        self.assertIn("already exists", response.json["message"])
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()
