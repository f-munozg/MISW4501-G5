import unittest, os
from flask import Flask
from flask_restful import Api
from models.models import Seller
from views.get_seller import GetSeller
from unittest.mock import patch, MagicMock

class GetSellerTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(GetSeller, '/sellers/seller')
        self.app = app.test_client()  
        self.app.testing = True 

    @patch("models.models.db.session")
    def test_get_seller(self, mock_db_session):
        seller = Seller(
            id = "c8b3a7ed-8a1e-4a5b-a299-7a5532e2b11b"
        )
        mock_db_session.query.return_value.filter.return_value.first.return_value = seller
        response = self.app.get('/sellers/seller?user_id=c8b3a7ed-8a1e-4a5b-a299-7a5532e2b11b')

        self.assertEqual(response.status_code, 200)

    def test_get_seller_invalid_seller_id(self):
        
        response = self.app.get('/sellers/seller?seller_id=1234')

        self.assertEqual(response.status_code, 400)
        
        self.assertEqual(response.data.decode(), '{"message": "invalid seller id"}\n')

    def test_get_seller_invalid_user_id(self):
        
        response = self.app.get('/sellers/seller?user_id=1234')

        self.assertEqual(response.status_code, 400)
        
        self.assertEqual(response.data.decode(), '{"message": "invalid user id"}\n')

    def test_get_seller_missing_query_parameters(self):
        
        response = self.app.get('/sellers/seller')

        self.assertEqual(response.status_code, 400)
        
        self.assertEqual(response.data.decode(), '{"message": "missing id"}\n')

    @patch("models.models.db.session")
    def test_get_seller_seller_not_found(self, mock_db_session):
        
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        response = self.app.get('/sellers/seller?seller_id=c8b3a7ed-8a1e-4a5b-a299-7a5532e2b11b')

        self.assertEqual(response.status_code, 404)
        
        self.assertEqual(response.data.decode(), '{"message": "seller not found"}\n')