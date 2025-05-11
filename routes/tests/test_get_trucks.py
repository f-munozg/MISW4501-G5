import unittest, os
from flask import Flask
from flask_restful import Api
from views.get_trucks import GetTrucks
from models.models import Truck
from unittest.mock import patch, MagicMock

class GetTrucksTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(GetTrucks, '/routes/trucks')
        self.app = app.test_client()  
        self.app.testing = True 

    @patch("models.models.db.session")
    def test_get_trucks(self, mock_db_session):
        routes = [Truck(id="35eaa088-d14a-48b2-a744-276c8b10824c")]
        mock_db_session.query.return_value.filter.return_value.all.return_value = routes
    
        response = self.app.get('/routes/trucks')
        
        self.assertEqual(response.status_code, 200)
        
    @patch("models.models.db.session")
    def test_get_trucks_filter_warehouse(self, mock_db_session):
        routes = [Truck(id="35eaa088-d14a-48b2-a744-276c8b10824c")]
        mock_db_session.query.return_value.filter.return_value.all.return_value = routes
    
        response = self.app.get('/routes/trucks?warehouse_id=35eaa088-d14a-48b2-a744-276c8b10824c')
        
        self.assertEqual(response.status_code, 200)

    def test_get_trucks_filter_warehouse_invalid_id(self):
        
        response = self.app.get('/routes/trucks?warehouse_id=35eaa088-d14a-48b2-a744-276c8b10824')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"message": "invalid warehouse id"})