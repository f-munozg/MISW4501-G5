import unittest, os
from flask import Flask, json
from flask_restful import Api
from models.models import Order
from views.create_order import CreateOrder
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import IntegrityError

class CreateOrderTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(CreateOrder, '/orders/order')
        self.app = app.test_client()  
        self.app.testing = True 

    @patch("requests.request")
    @patch("models.models.db.session")
    def test_create_order(self, mock_db_session, mock_requests):
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()
        mock_db_session.query.return_value.filter_by.return_value.first.side_effect = MagicMock()
        mock_requests.return_value.status_code = 200
        mock_requests.return_value.json.return_value = {
            "customer": {
                "id": "1313d313-e1f9-46ff-b616-05a841d5964f"
            }
        }

        response = self.app.post('/orders/order',
            data=json.dumps({
                "user_id": "9ebec3c3-3406-498b-be8e-c87a24774c55",
                "order_id": "9ebec3c3-3406-498b-be8e-c87a24774c55"
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 201)
        
    def test_create_order_with_missing_fields(self):
        
        response = self.app.post('/orders/order',
            data=json.dumps({
                "user_id": "9ebec3c3-3406-498b-be8e-c87a24774c55"
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 400)
        
        self.assertEqual(response.data.decode(), '{"message": "Missing required fields: order_id"}\n')


    def test_create_order_with_invalid_user_id(self):
        
        response = self.app.post('/orders/order',
            data=json.dumps({
                "user_id": "9ebec3c3-3406-498b-be8e-c87a24774c5",
                "order_id": "9ebec3c3-3406-498b-be8e-c87a24774c55"
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 400)
        
        self.assertEqual(response.data.decode(), '{"message": "invalid user id"}\n')


    def test_create_order_with_invalid_order_id(self):
        
        response = self.app.post('/orders/order',
            data=json.dumps({
                "user_id": "9ebec3c3-3406-498b-be8e-c87a24774c55",
                "order_id": "9ebec3c3-3406-498b-be8e-c87a24774c5"
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 400)
        
        self.assertEqual(response.data.decode(), '{"message": "invalid order id"}\n')


    @patch("requests.request")
    def test_create_order_with_users_api_error(self, mock_requests):
        mock_requests.return_value.status_code = 404
        mock_requests.return_value.json.return_value = {
            "message": "customer_not_found"
        }

        response = self.app.post('/orders/order',
            data=json.dumps({
                "user_id": "9ebec3c3-3406-498b-be8e-c87a24774c55",
                "order_id": "9ebec3c3-3406-498b-be8e-c87a24774c55"
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 404)

    @patch("requests.request")
    @patch("models.models.db.session")
    def test_create_order_with_no_pending_reserves(self, mock_db_session, mock_requests):

        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = None
        mock_requests.return_value.status_code = 200
        mock_requests.return_value.json.return_value = {
            "customer": {
                "id": "1313d313-e1f9-46ff-b616-05a841d5964f"
            }
        }

        response = self.app.post('/orders/order',
            data=json.dumps({
                "user_id": "9ebec3c3-3406-498b-be8e-c87a24774c55",
                "order_id": "9ebec3c3-3406-498b-be8e-c87a24774c55"
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 400),
        self.assertEqual(response.data.decode(), '{"message": "invalid reserve to activate"}\n')