import unittest, os
from flask import Flask
from flask_restful import Api
from models.models import Order
from views.get_order import GetOrder
from unittest.mock import patch, MagicMock

class GetOrderTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(GetOrder, '/orders/<order_id>')
        self.app = app.test_client()  
        self.app.testing = True 

    @patch("models.models.db.session")
    def test_get_orders(self, mock_db_session):
        order = Order(
            id = "c8b3a7ed-8a1e-4a5b-a299-7a5532e2b11b"
        )
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = order
        response = self.app.get('/orders/c8b3a7ed-8a1e-4a5b-a299-7a5532e2b11b')

        self.assertEqual(response.status_code, 200)

    def test_get_orders_missing_order_id(self):
        
        response = self.app.get('/orders/ ')

        self.assertEqual(response.status_code, 400)
        
        self.assertEqual(response.data.decode(), '{"message": "invalid order id"}\n')

    @patch("models.models.db.session")
    def test_get_orders_order_not_found(self, mock_db_session):
        
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = None
        response = self.app.get('/orders/c8b3a7ed-8a1e-4a5b-a299-7a5532e2b11b')

        self.assertEqual(response.status_code, 404)
        
        self.assertEqual(response.data.decode(), '{"message": "order not found"}\n')