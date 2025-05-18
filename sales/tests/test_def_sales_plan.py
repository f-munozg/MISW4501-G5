import unittest
import os
from unittest.mock import patch, MagicMock
from flask import json
from app import create_app
from sqlalchemy.exc import IntegrityError
from models.models import SalesPlan, PlanPeriod

class TestSalesPlan(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # UUIDs válidos para pruebas
        self.valid_seller_id = "d290f1ee-6c54-4b01-90e6-d701748f0851"
        self.valid_product_id = "1c3e3f36-cd99-4d60-8594-9cc971a928e5"

    def tearDown(self):
        self.app_context.pop()

    @patch("models.models.db.session")
    def test_create_sales_plan_success(self, mock_db_session):
        """Prueba la creación exitosa de un plan de ventas."""
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()

        payload = {
            "seller_id": self.valid_seller_id,
            "target": 10000,
            "product_id": self.valid_product_id,
            "period": "TRIMESTRAL"
        }

        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = None
        mock_db_session.query.return_value = mock_query

        response = self.client.post(
            "/sales-plans",
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
            "seller_id": self.valid_seller_id,
            "target": 10000,
        }

        response = self.client.post(
            "/sales-plans",
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required fields", response.json["message"])
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()

    @patch("models.models.db.session")
    def test_create_sales_plan_integrity_error(self, mock_db_session):
        """Prueba que maneja correctamente errores de integridad."""
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock(side_effect=IntegrityError(None, None, None))
        mock_db_session.rollback = MagicMock()

        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = None
        mock_db_session.query.return_value = mock_query

        payload = {
            "seller_id": self.valid_seller_id,
            "target": 10000,
            "product_id": self.valid_product_id,
            "period": "TRIMESTRAL"
        }

        response = self.client.post(
            "/sales-plans",
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 409)
        self.assertIn("Integrity error", response.json["message"])
        mock_db_session.rollback.assert_called_once()

    @patch("models.models.db.session")
    def test_create_sales_plan_duplicate_active(self, mock_db_session):
        """Prueba que no se pueda crear un plan activo duplicado para mismo vendedor y periodo."""
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = MagicMock()
        mock_db_session.query.return_value = mock_query

        payload = {
            "seller_id": self.valid_seller_id,
            "target": 10000,
            "product_id": self.valid_product_id,
            "period": "TRIMESTRAL"
        }

        response = self.client.post(
            "/sales-plans",
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 409)
        self.assertIn("already exists", response.json["message"])
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()

    def test_create_sales_plan_invalid_seller_id(self):
        """Prueba que valida correctamente un seller_id inválido."""
        payload = {
            "seller_id": "invalid-uuid",
            "target": 10000,
            "product_id": self.valid_product_id,
            "period": "TRIMESTRAL"
        }

        response = self.client.post(
            "/sales-plans",
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["message"], "invalid seller id")

    def test_create_sales_plan_invalid_product_id(self):
        """Prueba que valida correctamente un product_id inválido."""
        payload = {
            "seller_id": self.valid_seller_id,
            "target": 10000,
            "product_id": "invalid-uuid",
            "period": "TRIMESTRAL"
        }

        response = self.client.post(
            "/sales-plans",
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["message"], "invalid product id")

    def test_create_sales_plan_invalid_period(self):
        """Prueba que valida correctamente un periodo inválido."""
        payload = {
            "seller_id": self.valid_seller_id,
            "target": 10000,
            "product_id": self.valid_product_id,
            "period": "INVALID"
        }

        response = self.client.post(
            "/sales-plans",
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid period", response.json["message"])

    # Pruebas para el método GET
    @patch("models.models.db.session")
    def test_get_sales_plan_success(self, mock_db_session):
        """Prueba la obtención exitosa de un plan de ventas."""
        mock_plan = MagicMock()
        mock_plan.id = "550e8400-e29b-41d4-a716-446655440000"
        mock_plan.seller_id = self.valid_seller_id
        mock_plan.target = 10000
        mock_plan.product_id = self.valid_product_id
        mock_plan.period = PlanPeriod.TRIMESTRAL
        mock_plan.active = True

        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_plan
        mock_db_session.query.return_value = mock_query

        response = self.client.get(
            f"/sales-plans?seller_id={self.valid_seller_id}&period=TRIMESTRAL"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Sales plan retrieved successfully")
        self.assertEqual(response.json["sales_plan"]["seller_id"], self.valid_seller_id)

    def test_get_sales_plan_missing_params(self):
        """Prueba que falla si faltan parámetros requeridos."""
        response = self.client.get("/sales-plans")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required query parameters", response.json["message"])

    def test_get_sales_plan_invalid_seller_id(self):
        """Prueba que valida correctamente un seller_id inválido en GET."""
        response = self.client.get("/sales-plans?seller_id=invalid-uuid&period=TRIMESTRAL")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["message"], "invalid seller id")

    def test_get_sales_plan_invalid_period(self):
        """Prueba que valida correctamente un periodo inválido en GET."""
        response = self.client.get(
            f"/sales-plans?seller_id={self.valid_seller_id}&period=INVALID"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid period", response.json["message"])

    @patch("models.models.db.session")
    def test_get_sales_plan_not_found(self, mock_db_session):
        """Prueba que maneja correctamente cuando no se encuentra el plan."""
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = None
        mock_db_session.query.return_value = mock_query

        response = self.client.get(
            f"/sales-plans?seller_id={self.valid_seller_id}&period=TRIMESTRAL"
        )

        self.assertEqual(response.status_code, 404)
        self.assertIn("No active sales plan found", response.json["message"])
