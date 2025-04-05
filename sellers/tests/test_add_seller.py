import unittest
import os
from unittest.mock import patch, MagicMock
from app import create_app
from flask import json
from sqlalchemy.exc import IntegrityError

class TestAddSeller(unittest.TestCase):
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

    @patch("models.models.db.session")
    def test_create_seller_success(self, mock_db_session):
        """Prueba la creación exitosa de un vendedor."""
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()

        response = self.client.post(
            "/sellers/add",
            data=json.dumps({
                "identification_number": "123456",
                "name": "John Doe",
                "email": "john@example.com",
                "address": "Calle 80",
                "phone": "6015425568",
                "zone": "NORTE"
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["message"], "Seller created successfully")
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @patch("models.models.db.session")
    def test_create_seller_duplicate(self, mock_db_session):
        """Prueba un error al intentar crear un vendedor duplicado."""
        mock_db_session.add = MagicMock()
        mock_db_session.commit.side_effect = IntegrityError("test", "test", "test")

        response = self.client.post(
            "/sellers/add",
            data=json.dumps({
                "identification_number": "123456",
                "name": "John Doe",
                "email": "john@example.com",
                "address": "Calle 80",
                "phone": "6015425568",
                "zone": "NORTE"
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json["message"], "Seller is already registered")
        mock_db_session.add.assert_called_once()

    @patch("models.models.db.session")
    def test_create_seller_missing_data(self, mock_db_session):
        """Prueba un error cuando faltan datos obligatorios."""
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()

        response = self.client.post(
            "/sellers/add",
            data=json.dumps({
                "identification_number": "123456",
                "name": "John Doe"
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)

if __name__ == "__main__":
    unittest.main()
