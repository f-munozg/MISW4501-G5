import unittest, json
import os
from unittest.mock import patch, MagicMock
from flask import json
from requests.models import Response
from app import create_app
import uuid
from sqlalchemy.exc import IntegrityError

class TestAddSeller(unittest.TestCase):
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


    @patch("models.models.db.session")
    @patch("requests.request")
    def test_add_seller_with_customers(self, mock_requests, mock_db_session):
        """Debe crear exitosamente un vendedor con clientes"""
        role_id = str(uuid.uuid4())
        
        successful_user = {
                "message": "user created successfully",
                "id": str(uuid.uuid4())
                }

        successful_customer = {
            "message": "seller_assigned_successfully"
        }

        response_user = Response()
        response_user.status_code = 201
        response_user._content = json.dumps(successful_user).encode('utf-8')
        response_customer = Response()
        response_customer.status_code = 200
        response_customer._content = json.dumps(successful_customer).encode('utf-8')

        mock_requests.side_effect = response_user, response_customer

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
            "password": "1234",
            "customers": [ "d74d1c89-bf56-4391-9bbe-b878dc5ef149" ]
        }

        response = self.client.post("/sellers/add", json=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["message"], "Seller created successfully")


    @patch("models.models.db.session")
    @patch("requests.request")
    def test_add_seller_with_customers_error(self, mock_requests, mock_db_session):
        """Debe crear exitosamente un vendedor con clientes"""
        role_id = str(uuid.uuid4())
        
        successful_user = {
                "message": "user created successfully",
                "id": str(uuid.uuid4())
                }

        failed_customers = {
            "message": "error"
        }

        response_user = Response()
        response_user.status_code = 201
        response_user._content = json.dumps(successful_user).encode('utf-8')
        response_customer = Response()
        response_customer.status_code = 500
        response_customer._content = json.dumps(failed_customers).encode('utf-8')

        mock_requests.side_effect = response_user, response_customer

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
            "password": "1234",
            "customers": [ "d74d1c89-bf56-4391-9bbe-b878dc5ef149" ]
        }

        response = self.client.post("/sellers/add", json=data)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json["message"], "error")

        