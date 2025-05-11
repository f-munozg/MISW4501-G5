import unittest, os
from flask import Flask
from flask_restful import Api
from views.confirm_route import ConfirmRoute
from unittest.mock import patch, MagicMock

class ConfirmRouteTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(ConfirmRoute, '/routes/<route_id>/confirm')
        self.app = app.test_client()  
        self.app.testing = True 

    @patch("models.models.db.session")
    def test_confirm_route(self, mock_db_session):
        mock_db_session.commit = MagicMock()

        mock_db_session.query.return_value.filter.return_value.all.side_effect = ["a", "b"]

        response = self.app.put('/routes/35eaa088-d14a-48b2-a744-276c8b10824c/confirm')
        
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(response.data.decode(), '{"message": "route confirmed successfully"}\n')

    @patch("models.models.db.session")
    def test_confirm_confirmed_route(self, mock_db_session):
        mock_db_session.query = MagicMock()
        mock_db_session.commit = MagicMock()

        response = self.app.put('/routes/35eaa088-d14a-48b2-a744-276c8b10824c/confirm')
        
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(response.data.decode(), '{"message": "route already confirmed"}\n')

    def test_confirm_route_invalid_uuid(self):
        
        response = self.app.put('/routes/35eaa088-d14a-48b2-a744-276c8b10824/confirm')
        
        self.assertEqual(response.status_code, 400)
        
        
        self.assertEqual(response.data.decode(), '{"message": "invalid route id"}\n')

    @patch("models.models.db.session")
    def test_confirm_route_not_found(self, mock_db_session):
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        response = self.app.put('/routes/35eaa088-d14a-48b2-a744-276c8b10824c/confirm')
        
        self.assertEqual(response.status_code, 404)
        
        self.assertEqual(response.data.decode(), '{"message": "route not found"}\n')