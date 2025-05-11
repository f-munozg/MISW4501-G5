import unittest, os
from flask import Flask
from flask_restful import Api
from views.get_trucks_location import GetTrucksLocation
from models.models import Truck
from unittest.mock import patch, MagicMock

class GetTrucksLocationTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(GetTrucksLocation, '/routes/trucks/location')
        self.app = app.test_client()  
        self.app.testing = True 

    @patch("models.models.db.session")
    def test_get_truck_location(self, mock_db_session):
        trucks = [Truck(id="35eaa088-d14a-48b2-a744-276c8b10824c")]
        mock_db_session.query.return_value.all.return_value = trucks
    
        response = self.app.get('/routes/trucks/location')
        
        self.assertEqual(response.status_code, 200)
        