import unittest, os
from flask import Flask
from flask_restful import Api
from views.get_provider_products import GetProviderProducts
from unittest.mock import patch, MagicMock

class GetProviderProductsTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(GetProviderProducts, '/products/provider/<provider_id>')
        self.app = app.test_client()  
        self.app.testing = True 

    @patch("models.models.db.session")
    def test_get_provider_products(self, mock_db_session):
        mock_db_session.query = MagicMock()
        response = self.app.get('/products/provider/e85a8fd2-a836-4c5c-94bb-d55e73b4cd1e')
        
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(response.data.decode(), '{"provider_id": "e85a8fd2-a836-4c5c-94bb-d55e73b4cd1e", "products": []}\n')

    @patch("models.models.db.session")
    def test_get_provider_products_invalid_provider_id(self, mock_db_session):
        mock_db_session.query = MagicMock()
        response = self.app.get('/products/provider/e85a8fd2-a836-4c5c-94bb-d55e73b4cd1')
        
        self.assertEqual(response.status_code, 400)
        
        self.assertEqual(response.data.decode(), '{"message": "invalid provider id"}\n')