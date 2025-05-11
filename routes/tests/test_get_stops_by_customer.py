import unittest, os
from flask import Flask
from flask_restful import Api
from views.get_stops_by_customer import GetStopsByCustomer
from models.models import Route, RouteStop
from unittest.mock import patch, MagicMock

class GetStopsByCustomerTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(GetStopsByCustomer, '/routes/stops/customer/<customer_id>')
        self.app = app.test_client()  
        self.app.testing = True 

    @patch("models.models.db.session")
    def test_get_stops_by_customer(self, mock_db_session):
        routes = [RouteStop(id="35eaa088-d14a-48b2-a744-276c8b10824c")]
        mock_db_session.query.return_value.filter.return_value.all.return_value = routes
    
        response = self.app.get('/routes/stops/customer/35eaa088-d14a-48b2-a744-276c8b10824c')
        
        self.assertEqual(response.status_code, 200)
        

    def test_get_routes_invalid_customer_id(self):
        
        response = self.app.get('/routes/stops/customer/35eaa088-d14a-48b2-a744-276c8b10824')
        
        self.assertEqual(response.status_code, 400)
        
        self.assertEqual(response.data.decode(), '{"message": "invalid customer id"}\n')
