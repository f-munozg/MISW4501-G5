import unittest, os, json, base64
from flask import Flask
from flask_restful import Api
from models.models import Payment
from views.create_payment import CreatePayment
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import IntegrityError

class TestCreatePayment(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(CreatePayment, '/customers/payment')
        self.app = app.test_client()
        self.app.testing = True

    @patch("requests.put")
    @patch("requests.get")
    @patch("models.models.db.session")
    def test_create_payment_success(self, mock_db_session, mock_requests_get, mock_requests_put):
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()

        # Simula la respuesta del GET con el objeto completo de la orden
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = {
            "id": "9ebec3c3-3406-498b-be8e-c87a24774c55",
            "customer_id": "customer123",
            "seller_id": "seller123",
            "date_order": "2024-01-01",
            "date_delivery": "2024-01-10",
            "status": "Pending"
        }

        # Simula la respuesta exitosa del PUT
        mock_requests_put.return_value.status_code = 200

        response = self.app.post('/customers/payment',
            data=json.dumps({
                "order_id": "9ebec3c3-3406-498b-be8e-c87a24774c55",
                "type_payment": "Completo",
                "mean_payment": "Transferencia bancaria",
                "voucher_payment": base64.b64encode(b"fake_image_data").decode("utf-8")
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertIn("Payment created successfully", response.data.decode())

        # Verifica que se hizo el PUT con el JSON correcto
        mock_requests_put.assert_called_once_with(
            'http://localhost:5000/orders/updateStatus',
            json={
                "id": "9ebec3c3-3406-498b-be8e-c87a24774c55",
                "customer_id": "customer123",
                "seller_id": "seller123",
                "date_order": "2024-01-01",
                "date_delivery": "2024-01-10",
                "status": "Pagado"
            }
        )

    def test_create_payment_missing_fields(self):
        response = self.app.post('/customers/payment',
            data=json.dumps({
                "order_id": "9ebec3c3-3406-498b-be8e-c87a24774c55"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required fields", response.data.decode())

    def test_create_payment_invalid_order_id_format(self):
        response = self.app.post('/customers/payment',
            data=json.dumps({
                "order_id": "invalid-uuid",
                "type_payment": "Completo",
                "mean_payment": "Transferencia bancaria",
                "voucher_payment": base64.b64encode(b"fake_image_data").decode("utf-8")
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid order_id format", response.data.decode())

    @patch("requests.get")
    def test_create_payment_nonexistent_order_id(self, mock_requests_get):
        mock_requests_get.return_value.status_code = 404

        response = self.app.post('/customers/payment',
            data=json.dumps({
                "order_id": "9ebec3c3-3406-498b-be8e-c87a24774c55",
                "type_payment": "Completo",
                "mean_payment": "Transferencia bancaria",
                "voucher_payment": base64.b64encode(b"fake_image_data").decode("utf-8")
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 404)
        self.assertIn("Invalid or non-existent order_id", response.data.decode())

    @patch("requests.get")
    def test_create_payment_invalid_base64(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response

        response = self.app.post('/customers/payment',
            data=json.dumps({
                "order_id": "9ebec3c3-3406-498b-be8e-c87a24774c55",
                "type_payment": "Completo",
                "mean_payment": "Transferencia bancaria",
                "voucher_payment": "not_base64_string!"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid base64 format", response.data.decode())

    @patch("requests.get")
    def test_create_payment_invalid_enum(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response

        response = self.app.post('/customers/payment',
            data=json.dumps({
                "order_id": "9ebec3c3-3406-498b-be8e-c87a24774c55",
                "type_payment": "INVALID",
                "mean_payment": "Transferencia bancaria",
                "voucher_payment": base64.b64encode(b"fake_image_data").decode("utf-8")
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid type_payment or mean_payment", response.data.decode())
