import unittest, os
from flask import Flask
from flask_restful import Api
from views.get_customer import GetCustomer
from models.models import Customer
from unittest.mock import patch, MagicMock

class GetCustomerTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(GetCustomer, '/customer/<user_id>')
        self.app = app.test_client()  
        self.app.testing = True 

    @patch("models.models.db.session")
    def test_get_customer(self, mock_db_session):
        mock_db_session.query = MagicMock()
        response = self.app.get('/customer/9ebec3c3-3406-498b-be8e-c87a24774c55')
        
        self.assertEqual(response.status_code, 200)

    def test_get_customer_invalid_user_id(self):
        response = self.app.get('/customer/XXXXXXX')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.decode(), '{"message": "invalid user id"}\n')

    @patch("models.models.db.session")
    def test_get_customer_not_found(self, mock_db_session):
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = None
        response = self.app.get('/customer/9ebec3c3-3406-498b-be8e-c87a24774c55')
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data.decode(), '{"message": "customer not found"}\n')


    @patch("models.models.db.session")
    def test_get_customer_store_not_found(self, mock_db_session):
        customer = Customer(id = "9ebec3c3-3406-498b-be8e-c87a24774c55")
        mock_db_session.query.return_value.filter_by.return_value.first.side_effect = [customer, None]
        response = self.app.get('/customer/9ebec3c3-3406-498b-be8e-c87a24774c55')
        
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data.decode(), '{"message": "store not found"}\n')

