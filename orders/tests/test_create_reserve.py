import unittest, os
from flask import Flask, json
from flask_restful import Api
from models.models import Order
from views.create_reserve import CreateReserve
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import IntegrityError

class CreateReserveTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(CreateReserve, '/orders/reserve')
        self.app = app.test_client()  
        self.app.testing = True 

    @patch("views.create_reserve.call_stock_service")  # 👈 este es importante
    @patch("requests.request")  # mock para el request GET a customers
    @patch("models.models.db.session")
    def test_create_reserve(self, mock_db_session, mock_requests, mock_call_stock):
        # Mock DB
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()
        mock_db_session.flush = MagicMock()
        mock_db_session.rollback = MagicMock()
        mock_db_session.query.return_value.filter_by.return_value.all.return_value = []

        # Mock GET /customers/{id}
        mock_requests.return_value.status_code = 200
        mock_requests.return_value.json.return_value = {
            "customer": {
                "id": "1313d313-e1f9-46ff-b616-05a841d5964f"
            }
        }

        # Mock call_stock_service
        mock_call_stock.return_value = (
            200,
            {"warehouse_id": "e78de541-09fb-4f4e-a3f4-99cc4c0e94a4"}
        )

        # Realizamos la solicitud
        response = self.app.post('/orders/reserve',
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
        self.assertIn("reserve created successfully", response.get_data(as_text=True))


    def test_create_reserve_missing_fields(self):
        response = self.app.post('/orders/reserve',
            data=json.dumps({
                "user_id": "9ebec3c3-3406-498b-be8e-c87a24774c55",
                "seller_id": "9ebec3c3-3406-498b-be8e-c87a24774c55"
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.decode(), '{"message": "Missing required fields: products"}\n')

    def test_create_reserve_invalid_user_id(self):
        response = self.app.post('/orders/reserve',
            data=json.dumps({
                "user_id": "9ebec3c3-3406-498b-be8e-c87a24774c5",
                "seller_id": "9ebec3c3-3406-498b-be8e-c87a24774c55",
                "products": [
                    {
                        "id": ""
                    }
                ]
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.decode(), '{"message": "invalid user id"}\n')
        
        
    @patch("requests.request")
    @patch("models.models.db.session")
    def test_create_reserve_users_api_error(self, mock_db_session, mock_requests):
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()
        mock_requests.return_value.status_code = 404
        mock_requests.return_value.json.return_value = {
            "message": "user_not_found"
        }

        response = self.app.post('/orders/reserve',
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
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data.decode(), '{"message": "user_not_found"}\n')


    @patch("requests.request")
    @patch("models.models.db.session")
    def test_create_reserve_existing_reserve_error(self, mock_db_session, mock_requests):
        orderList = [Order(), Order()]
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()
        mock_db_session.query.return_value.filter_by.return_value.all.return_value = orderList
        mock_requests.return_value.status_code = 200
        mock_requests.return_value.json.return_value = {
            "customer": {
                "id": "1313d313-e1f9-46ff-b616-05a841d5964f"
            }
        }

        response = self.app.post('/orders/reserve',
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
        
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data.decode(), '{"message": "customer already has a reserve"}\n')
