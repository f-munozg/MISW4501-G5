import unittest, os
from datetime import datetime
from flask import Flask
from flask_restful import Api
from models.models import Order, Payments
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
    def test_get_order_with_payments(self, mock_db_session):
        order_id = "c8b3a7ed-8a1e-4a5b-a299-7a5532e2b11b"
        order = Order(
            id=order_id,
            customer_id="cust123",
            seller_id="seller456",
            date_order=datetime.now(),
            date_delivery=datetime.now(),
            status="delivered",
            order_total=100.0,
            status_payment="partial"
        )
        
        payment = Payments(
            id="pay123",
            order_id=order_id,
            total=100.0,
            balance=30.0,
            payment_date=datetime.now()
        )
        
        order_mock = MagicMock()
        order_mock.filter_by.return_value.first.return_value = order
        
        payments_mock = MagicMock()
        payments_mock.filter.return_value.order_by.return_value.first.return_value = payment
        
        mock_db_session.query.side_effect = [order_mock, payments_mock]
        
        response = self.app.get(f'/orders/{order_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        
        self.assertEqual(response_data["payment_summary"]["total_amount"], 100.0)
        self.assertEqual(response_data["payment_summary"]["paid_amount"], 70.0)
        self.assertEqual(response_data["payment_summary"]["pending_balance"], 30.0)

    @patch("models.models.db.session")
    def test_get_order_without_payments(self, mock_db_session):
        order_id = "c8b3a7ed-8a1e-4a5b-a299-7a5532e2b11b"
        order = Order(
            id=order_id,
            customer_id="cust123",
            seller_id="seller456",
            date_order=datetime.now(),
            date_delivery=datetime.now(),
            status="delivered",
            order_total=150.0,
            status_payment="pending"
        )
        
        order_mock = MagicMock()
        order_mock.filter_by.return_value.first.return_value = order
        
        payments_mock = MagicMock()
        payments_mock.filter.return_value.order_by.return_value.first.return_value = None
        
        mock_db_session.query.side_effect = [order_mock, payments_mock]
        
        response = self.app.get(f'/orders/{order_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        
        self.assertEqual(response_data["payment_summary"]["total_amount"], 150.0)
        self.assertEqual(response_data["payment_summary"]["paid_amount"], 0.0)
        self.assertEqual(response_data["payment_summary"]["pending_balance"], 150.0)
        self.assertIsNone(response_data["payment_summary"]["last_payment_date"])

    @patch("models.models.db.session")
    def test_get_orders(self, mock_db_session):
        order = Order(id = "c8b3a7ed-8a1e-4a5b-a299-7a5532e2b11b")
        
        order_mock = MagicMock()
        order_mock.filter_by.return_value.first.return_value = order
        
        payments_mock = MagicMock()
        payments_mock.filter.return_value.order_by.return_value.first.return_value = None
        
        mock_db_session.query.side_effect = [order_mock, payments_mock]
        
        response = self.app.get('/orders/c8b3a7ed-8a1e-4a5b-a299-7a5532e2b11b')
        self.assertEqual(response.status_code, 200)

    def test_get_orders_missing_order_id(self):
        response = self.app.get('/orders/ ')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.decode(), '{"message": "invalid order id"}\n')
        
    @patch("models.models.db.session")
    def test_get_orders_order_not_found(self, mock_db_session):
        order_mock = MagicMock()
        order_mock.filter_by.return_value.first.return_value = None
        mock_db_session.query.return_value = order_mock
        
        response = self.app.get('/orders/c8b3a7ed-8a1e-4a5b-a299-7a5532e2b11b')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data.decode(), '{"message": "order not found"}\n')