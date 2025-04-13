import unittest, os
from flask import Flask
from flask_restful import Api
from views.get_customer_orders import GetCustomerOrders
from unittest.mock import patch, MagicMock

class GetOrdersTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(GetCustomerOrders, '/orders/<user_id>')
        self.app = app.test_client()  
        self.app.testing = True 

    @patch("requests.request")
    @patch("models.models.db.session")
    def test_get_customer_orders(self, mock_db_session, mock_requests):
        mock_requests.return_value.status_code = 200
        mock_requests.return_value.json.return_value = {
            "customer": {
                "id": "1313d313-e1f9-46ff-b616-05a841d5964f"
            }
        }
        mock_db_session.query = MagicMock()
        response = self.app.get('/orders/9ebec3c3-3406-498b-be8e-c87a24774c55')
        
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(response.data.decode(), '{"orders": []}\n')

    def test_get_orders_invalid_user_id(self):
    
        response = self.app.get('/orders/ ')
        
        self.assertEqual(response.status_code, 400)
        
        self.assertEqual(response.data.decode(), '{"message": "invalid user id"}\n')

    @patch("requests.request")
    @patch("models.models.db.session")
    def test_get_customer_orders_users_api_error(self, mock_db_session, mock_requests):
        mock_requests.return_value.status_code = 404
        mock_requests.return_value.json.return_value = {
            "message": "user_not_found"
        }
        mock_db_session.query = MagicMock()
        response = self.app.get('/orders/9ebec3c3-3406-498b-be8e-c87a24774c55')
        
        self.assertEqual(response.status_code, 404)
        
        self.assertEqual(response.data.decode(), '{"message": "user_not_found"}\n')