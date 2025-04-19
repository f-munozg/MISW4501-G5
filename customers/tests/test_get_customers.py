import unittest, os, uuid
from flask import Flask
from flask_restful import Api
from views.get_customers import GetCustomers
from models.models import Customer
from unittest.mock import patch, MagicMock

class GetCustomersTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(GetCustomers, '/customers')
        self.app = app.test_client()  
        self.app.testing = True 

    @patch("models.models.db.session")
    def test_get_customers(self, mock_db_session):
        mock_db_session.query = MagicMock()
        response = self.app.get('/customers')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), '{"customers": []}\n')

    @patch("models.models.db.session")
    def test_get_available_customers(self, mock_db_session):
        mock_db_session.query = MagicMock()
        response = self.app.get('/customers?status=available')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), '{"customers": []}\n')


    @patch("models.models.db.session")
    def test_get_customers_by_seller_id(self, mock_db_session):
        mock_db_session.query = MagicMock()
        response = self.app.get('/customers?seller_id=278caa6b-fa76-4193-80ed-7fc2a814ef3f')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), '{"customers": []}\n')

    def test_get_customers_by_seller_id_with_invalid_id(self):
        response = self.app.get('/customers?seller_id=available')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.decode(), '{"message": "invalid seller id"}\n')


    @patch("requests.request")
    @patch("models.models.db.session")
    def test_get_customers_by_seller_user_id(self, mock_db_session, mock_requests):
        mock_db_session.query = MagicMock()
        mock_requests.return_value.status_code = 200
        mock_requests.return_value.json.return_value = {
            "seller": {
                "id": str(uuid.uuid4())
            }
        }

        response = self.app.get('/customers?seller_user_id=278caa6b-fa76-4193-80ed-7fc2a814ef3f')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), '{"customers": []}\n')

    def test_get_customers_by_seller_user_id_with_invalid_id(self):
        response = self.app.get('/customers?seller_user_id=available')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.decode(), '{"message": "invalid user id"}\n')


    @patch("requests.request")
    def test_get_customers_by_seller_user_id_with_users_api_error(self, mock_requests):
        mock_requests.return_value.status_code = 500
        mock_requests.return_value.json.return_value = {
            "message": "internal server error"
        }

        response = self.app.get('/customers?seller_user_id=278caa6b-fa76-4193-80ed-7fc2a814ef3f')

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data.decode(), '{"message": "internal server error"}\n')