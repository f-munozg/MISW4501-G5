import unittest, os
from flask import Flask, json
from flask_restful import Api
from views.update_customer import UpdateCustomer
from models.models import Customer, Store
from unittest.mock import patch, MagicMock

class UpdateCustomerTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(UpdateCustomer, '/customer/<user_id>')
        self.app = app.test_client()  
        self.app.testing = True 

    @patch("models.models.db.session")
    def test_update_customer(self, mock_db_session):
        mock_db_session.query = MagicMock()
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()

        response = self.app.put(
            '/customer/9ebec3c3-3406-498b-be8e-c87a24774c55',
            data=json.dumps({
                "name": "usuario 1", 
                "email": "mail1@mail.com", 
                "identification_number": "12345512312", 
                "store_id_number": "1245531234-1", 
                "store_address": "calle carrera", 
                "store_phone": "1339495921"
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 202)

    def test_update_customer(self):
        response = self.app.put(
            '/customer/9ebec3c3-3406-498b-be8e-c87a24774c55',
            data=json.dumps({
                "name": "usuario 1", 
                "email": "mail1@mail.com", 
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.decode(), '{"message": "Missing required fields: ' \
        'identification_number, store_id_number, store_address, store_phone"}\n')

    def test_update_customer_invalid_user_id(self):
        response = self.app.put(
            '/customer/XXXXXXX',
            data=json.dumps({
                "name": "usuario 1", 
                "email": "mail1@mail.com", 
                "identification_number": "12345512312", 
                "store_id_number": "1245531234-1", 
                "store_address": "calle carrera", 
                "store_phone": "1339495921"
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.decode(), '{"message": "Invalid user ID"}\n')

    @patch("models.models.db.session")
    def test_update_customer_user_not_found(self, mock_db_session):
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = None
        response = self.app.put(
            '/customer/9ebec3c3-3406-498b-be8e-c87a24774c55',
            data=json.dumps({
                "name": "usuario 1", 
                "email": "mail1@mail.com", 
                "identification_number": "12345512312", 
                "store_id_number": "1245531234-1", 
                "store_address": "calle carrera", 
                "store_phone": "1339495921"
            }),
            content_type="application/json"
            )
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data.decode(), '{"message": "invalid user id"}\n')


    @patch("models.models.db.session")
    def test_update_customer_customer_not_found(self, mock_db_session):
        customer = Customer(id = "9ebec3c3-3406-498b-be8e-c87a24774c55")
        mock_db_session.query.return_value.filter_by.return_value.first.side_effect = [customer, None]
        response = self.app.put(
            '/customer/9ebec3c3-3406-498b-be8e-c87a24774c55',
            data=json.dumps({
                "name": "usuario 1", 
                "email": "mail1@mail.com", 
                "identification_number": "12345512312", 
                "store_id_number": "1245531234-1", 
                "store_address": "calle carrera", 
                "store_phone": "1339495921"
            }),
            content_type="application/json"
            )
        
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data.decode(), '{"message": "customer not found"}\n')

    @patch("models.models.db.session")
    def test_update_customer_store_not_found(self, mock_db_session):
        customer = Customer(id = "9ebec3c3-3406-498b-be8e-c87a24774c55")
        store = Store()
        mock_db_session.query.return_value.filter_by.return_value.first.side_effect = [customer, store, None]
        response = self.app.put(
            '/customer/9ebec3c3-3406-498b-be8e-c87a24774c55',
            data=json.dumps({
                "name": "usuario 1", 
                "email": "mail1@mail.com", 
                "identification_number": "12345512312", 
                "store_id_number": "1245531234-1", 
                "store_address": "calle carrera", 
                "store_phone": "1339495921"
            }),
            content_type="application/json"
            )
        
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data.decode(), '{"message": "store not found"}\n')

