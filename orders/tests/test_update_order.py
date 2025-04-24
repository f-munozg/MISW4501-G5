import unittest
import os
from unittest.mock import patch, MagicMock
from flask import json
from app import create_app

class TestUpdateOrderStatus(unittest.TestCase):
    def setUp(self):
        """Configura la aplicación de prueba."""
        os.environ["TESTING"] = "true"
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()

        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Elimina el contexto de la aplicación después de cada prueba."""
        self.app_context.pop()

    def test_update_order_status_missing_fields(self):
        """Prueba cuando faltan campos obligatorios."""
        response = self.client.put(
            "/order/updateStatus",
            data=json.dumps({"order_id": "some-id"}),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("order_id and status are required", response.json["message"])

    def test_update_order_status_invalid_uuid(self):
        """Prueba cuando el UUID no es válido."""
        response = self.client.put(
            "/order/updateStatus",
            data=json.dumps({
                "order_id": "not-a-valid-uuid",
                "status": "shipped"
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid order ID format", response.json["message"])