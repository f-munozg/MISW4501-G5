import unittest, os
from flask import Flask
from flask_restful import Api
from views.get_products import GetProducts
from unittest.mock import patch, MagicMock

class GetProductsTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(GetProducts, '/products')
        self.app = app.test_client()  
        self.app.testing = True 

    @patch("models.models.db.session")
    def test_get_products(self, mock_db_session):
        mock_db_session.query = MagicMock()
        response = self.app.get('/products')
        
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(response.data.decode(), '{"products": []}\n')