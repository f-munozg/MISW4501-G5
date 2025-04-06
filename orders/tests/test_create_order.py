import unittest, os
from flask import Flask, json
from flask_restful import Api
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
    def test_create_user(self, mock_db_session, mock_requests):
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()
        mock_requests.return_value.status_code = 200
        mock_requests.return_value.json.return_value = {
            "customer": {
                "id": "1313d313-e1f9-46ff-b616-05a841d5964f"
            }
        }

        response = self.app.post('/orders/order',
            data=json.dumps({
                "user_id": "9ebec3c3-3406-498b-be8e-c87a24774c55",
                "seller_id": "9ebec3c3-3406-498b-be8e-c87a24774c55",
                "products": [
                    {
                        "id": "e7881a59-ff42-4220-bc7d-56ab036cafe4",
                        "quantity": 200
                    },
                    {
                        "id": "e126c03e-0de5-4631-932f-f34b5c5391d2",
                        "quantity": 100
                    }
                ]
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 201)
        

'''

    def test_create_user_with_missing_fields(self):
        
        response = self.app.post('/users/user',
            data=json.dumps({
                "username": "username",
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 400)
        
        self.assertEqual(response.data.decode(), '{"message": "Missing required fields: ' \
        'password, email, role"}\n')
        
    def test_create_user_invalid_role_id(self):
        
        response = self.app.post('/users/user',
            data=json.dumps({
                "username": "username",
                "password": "password123",
                "email": "mail@mail.com",
                "role": "Admin"
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 400)
        
        self.assertEqual(response.data.decode(), '{"message": "Invalid role ID"}\n')

    @patch("models.models.db.session")
    def test_create_user_already_exists(self, mock_db_session):
        mock_db_session.add = MagicMock()
        mock_db_session.commit.side_effect = IntegrityError("test", "test", "test")

        response = self.app.post('/users/user',
            data=json.dumps({
                "username": "username",
                "password": "password123",
                "email": "mail@mail.com",
                "role": "cc4a4702-3d00-4a1f-9474-d8ff331485a7"
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 409)
        
        self.assertEqual(response.data.decode(), '{"message": "user is already registered"}\n')


'''