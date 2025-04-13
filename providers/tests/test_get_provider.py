import unittest, os
from flask import Flask
from flask_restful import Api
from views.get_provider import GetProvider
from unittest.mock import patch, MagicMock

class GetProviderTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(GetProvider, '/provider/<provider_id>')
        self.app = app.test_client()  
        self.app.testing = True 

    @patch("requests.request")
    @patch("models.models.db.session")
    def test_get_provider(self, mock_db_session, mock_requests):
        mock_db_session.query = MagicMock()
        mock_requests.return_value.status_code = 200
        mock_requests.return_value.json.return_value = {
            "provider": "e85a8fd2-a836-4c5c-94bb-d55e73b4cd1e",
            "products": [
                {
                    "sku": "SKU-124",
                    "id": "a558ccb7-c6e4-4397-b0f0-59a6cd4b0e82"
                },
                {
                    "sku": "SKU-123",
                    "id": "a558ccb7-c6e4-4397-b0f0-59a6cd4b0e81"
                }
            ]
        }
        response = self.app.get('/provider/e85a8fd2-a836-4c5c-94bb-d55e73b4cd1e')
        
        self.assertEqual(response.status_code, 200)

    def test_get_provider_invalid_provider_id(self):
        response = self.app.get('/provider/e85a8fd2-a836-4c5c-94bb-d55e73b4cd1')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.decode(), '{"message": "invalid provider id"}\n')

    @patch("models.models.db.session")
    def test_get_provider_provider_not_found(self, mock_db_session):
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = None
        
        response = self.app.get('/provider/e85a8fd2-a836-4c5c-94bb-d55e73b4cd1e')
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data.decode(), '{"message": "provider not found"}\n')


    @patch("requests.request")
    @patch("models.models.db.session")
    def test_get_provider_products_api_error(self, mock_db_session, mock_requests):
        mock_db_session.query = MagicMock()
        mock_requests.return_value.status_code = 500
        mock_requests.return_value.json.return_value = {
            "message": "internal server error"
        }
        response = self.app.get('/provider/e85a8fd2-a836-4c5c-94bb-d55e73b4cd1e')
        
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data.decode(), '{"message": "internal server error"}\n')

