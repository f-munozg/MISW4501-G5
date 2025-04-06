import unittest
from unittest.mock import patch, MagicMock
from flask import json
from app import create_app
import uuid
from sqlalchemy.exc import IntegrityError

class TestAddSeller(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch("models.models.db.session")
    def test_missing_required_fields(self, mock_db_session):
        """Debe fallar si faltan campos requeridos"""
        response = self.client.post("/sellers/add", json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required fields", response.json["message"])

    @patch("models.models.db.session")
    def test_invalid_zone(self, mock_db_session):
        """Debe fallar si la zona es inválida"""
        data = {
            "identification_number": "123456",
            "email": "test@example.com",
            "name": "Nombre Prueba",
            "zone": "CENTRO",
            "username": "user_test",
            "password": "1234"
        }
        response = self.client.post("/sellers/add", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid zone", response.json["message"])

    @patch("models.models.db.session")
    @patch("requests.request")
    def test_successful_seller_creation(self, mock_requests, mock_db_session):
        """Debe crear exitosamente un vendedor"""
        role_id = str(uuid.uuid4())
        
        mock_requests.return_value.status_code = 201
        mock_requests.return_value.json.return_value = {
            "message": "user created successfully",
            "id": str(uuid.uuid4())
        }

        mock_role = MagicMock()
        mock_role.id = role_id
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_role
        mock_db_session.query.return_value = mock_query

        data = {
            "identification_number": "123456",
            "email": "test@example.com",
            "name": "Nombre Prueba",
            "zone": "norte",
            "username": "user_test",
            "password": "1234"
        }

        response = self.client.post("/sellers/add", json=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["message"], "Seller created successfully")

    @patch("models.models.db.session")
    @patch("requests.request")
    def test_user_creation_fails(self, mock_requests, mock_db_session):
        """Debe devolver error si el servicio de usuario falla"""
        mock_requests.return_value.status_code = 409
        mock_requests.return_value.json.return_value = {
            "message": "user is already registered"
        }

        mock_role = MagicMock()
        mock_role.id = str(uuid.uuid4())
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_role
        mock_db_session.query.return_value = mock_query

        data = {
            "identification_number": "123456",
            "email": "test@example.com",
            "name": "Nombre Prueba",
            "zone": "sur",
            "username": "user_test",
            "password": "1234"
        }

        response = self.client.post("/sellers/add", json=data)
        self.assertEqual(response.status_code, 409)
        self.assertIn("user is already registered", response.json["message"])

    @patch("models.models.db.session")
    @patch("requests.request")
    def test_duplicate_seller(self, mock_requests, mock_db_session):
        """Debe fallar si el vendedor ya está registrado (IntegrityError)"""
        mock_requests.return_value.status_code = 201
        mock_requests.return_value.json.return_value = {
            "message": "user created successfully",
            "id": str(uuid.uuid4())
        }

        mock_role = MagicMock()
        mock_role.id = str(uuid.uuid4())
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_role
        mock_db_session.query.return_value = mock_query

        mock_db_session.add.return_value = None
        mock_db_session.commit.side_effect = IntegrityError("Mock IntegrityError", None, None)

        data = {
            "identification_number": "123456",
            "email": "test@example.com",
            "name": "Nombre Prueba",
            "zone": "oriente",
            "username": "user_test",
            "password": "1234"
        }

        response = self.client.post("/sellers/add", json=data)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json["message"], "Seller is already registered")

if __name__ == "__main__":
    unittest.main()
