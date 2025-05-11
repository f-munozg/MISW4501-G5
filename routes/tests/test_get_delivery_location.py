import unittest, os
from flask import Flask
from flask_restful import Api
from views.get_delivery_location import GetDeliveryLocation
from models.models import Route
from unittest.mock import patch, MagicMock

class GetDeliveryLocationTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(GetDeliveryLocation, '/routes/<order_id>/location')
        self.app = app.test_client()  
        self.app.testing = True 

    @patch("models.models.db.session")
    def test_get_delivery_location(self, mock_db_session):
        mock_db_session.commit = MagicMock()

        mock_db_session.query.return_value.filter.return_value.all.side_effect = ["a", "b"]

        response = self.app.get('/routes/35eaa088-d14a-48b2-a744-276c8b10824c/location')
        
        self.assertEqual(response.status_code, 200)
        

    def test_get_delivery_location_invalid_uuid(self):
        
        response = self.app.get('/routes/35eaa088-d14a-48b2-a744-276c8b10824/location')
        
        self.assertEqual(response.status_code, 400)
        
        self.assertEqual(response.data.decode(), '{"message": "invalid order id"}\n')

    @patch("models.models.db.session")
    def test_get_delivery_location_route_not_found(self, mock_db_session):
        mock_db_session.query.return_value.join.return_value.filter.return_value.first.return_value = None
        
        response = self.app.get('/routes/35eaa088-d14a-48b2-a744-276c8b10824c/location')
        
        self.assertEqual(response.status_code, 404)
        
        self.assertEqual(response.data.decode(), '{"message": "active route not found"}\n')


    @patch("models.models.db.session")
    def test_get_delivery_location_truck_not_found(self, mock_db_session):
        route = Route(
            id = "35eaa088-d14a-48b2-a744-276c8b10824c"
        )
        mock_db_session.query.return_value.join.return_value.filter.return_value.first.return_value = route
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = None
        
        response = self.app.get('/routes/35eaa088-d14a-48b2-a744-276c8b10824c/location')
        
        self.assertEqual(response.status_code, 500)
        
        self.assertEqual(response.data.decode(), '{"message": "error getting truck info"}\n')