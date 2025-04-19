import unittest, os, uuid
from flask import Flask, json
from flask_restful import Api
from views.log_visit import LogVisit
from unittest.mock import patch, MagicMock

class LogVisitTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(LogVisit, '/sales/log_visit')
        self.app = app.test_client()
        self.app.testing = True 

    @patch('requests.request')
    @patch("models.models.db.session")
    def test_log_visit(self, mock_db_session, mock_requests):
        mock_db_session.query = MagicMock()
        mock_requests.return_value.status_code = 200
        mock_requests.return_value.json.return_value = {
            "seller": {
                "id": str(uuid.uuid4())
            }
        }
        response = self.app.post(
            '/sales/log_visit',
            data=json.dumps({
                "customer_id": "fd6472db-cf25-48b2-b4ab-5e9978c878d6", 
                "user_id": "fd6472db-cf25-48b2-b4ab-5e9978c878d6",
                "store_address": "store address",
                "zone": "NORTE",
                "visit_status": "Realizada",
                "visit_result": "PEDIDO",
                "observations": "success"
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 201)

    def test_log_visit_missing_fields(self):
        response = self.app.post(
            '/sales/log_visit',
            data=json.dumps({
                "customer_id": "fd6472db-cf25-48b2-b4ab-5e9978c878d6", 
                "store_address": "store address",
                "zone": "NORTE",
                "visit_status": "Realizada",
                "visit_result": "PEDIDO",
                "observations": "success"
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.decode(), '{"message": "Missing required fields: user_id"}\n')


    def test_log_visit_invalid_user_id(self):
        response = self.app.post(
            '/sales/log_visit',
            data=json.dumps({
                "customer_id": "fd6472db-cf25-48b2-b4ab-5e9978c878d6", 
                "user_id": "fd6472db-cf25-48b2-b4ab-5e9978c878d", 
                "store_address": "store address",
                "zone": "NORTE",
                "visit_status": "Realizada",
                "visit_result": "PEDIDO",
                "observations": "success"
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.decode(), '{"message": "invalid user id"}\n')


    @patch('requests.request')
    @patch("models.models.db.session")
    def test_log_visit_sellers_api_error(self, mock_db_session, mock_requests):
        mock_db_session.query = MagicMock()
        mock_requests.return_value.status_code = 500
        mock_requests.return_value.json.return_value = {
            "message": "internal server error"
        }
        response = self.app.post(
            '/sales/log_visit',
            data=json.dumps({
                "customer_id": "fd6472db-cf25-48b2-b4ab-5e9978c878d6", 
                "user_id": "fd6472db-cf25-48b2-b4ab-5e9978c878d6",
                "store_address": "store address",
                "zone": "NORTE",
                "visit_status": "Realizada",
                "visit_result": "PEDIDO",
                "observations": "success"
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data.decode(), '{"message": "internal server error"}\n')