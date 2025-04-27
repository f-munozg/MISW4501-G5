import unittest, os
from flask import Flask, json
from flask_restful import Api
from views.assign_seller import AssignSeller
from models.models import Customer
from unittest.mock import patch, MagicMock

class AssignSellerTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(AssignSeller, '/customer/assign_seller')
        self.app = app.test_client()  
        self.app.testing = True 

    @patch("models.models.db.session")
    def test_assign_seller(self, mock_db_session):
        mock_db_session.query = MagicMock()
        response = self.app.post(
            '/customer/assign_seller',
            data=json.dumps({
                "customers": [
                    "4f721095-b922-45d1-8e94-802e6dfbaf76",
                    "fd6472db-cf25-48b2-b4ab-5e9978c878d5"
                ],
                "seller_id": "fd6472db-cf25-48b2-b4ab-5e9978c878d6"
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 200)

    def test_get_customer_missing_fields(self):
        response = self.app.post(
            '/customer/assign_seller',
            data=json.dumps({
                "seller_id": "fd6472db-cf25-48b2-b4ab-5e9978c878d6"
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.decode(), '{"message": "Missing required fields: customers"}\n')

