import unittest, os
from flask import Flask
from flask_restful import Api
from views.get_routes import GetRoutes
from models.models import Route, RouteStop
from unittest.mock import patch, MagicMock

class GetRoutesTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(GetRoutes, '/routes')
        self.app = app.test_client()  
        self.app.testing = True 

    @patch("models.models.db.session")
    def test_get_routes(self, mock_db_session):
        routes = [Route(id="35eaa088-d14a-48b2-a744-276c8b10824c")]
        mock_db_session.query.return_value.filter.return_value.all.return_value = routes
    
        response = self.app.get('/routes')
        
        self.assertEqual(response.status_code, 200)
        

    @patch("models.models.db.session")
    def test_get_routes_all_filters(self, mock_db_session):
        routes = [Route(id="35eaa088-d14a-48b2-a744-276c8b10824c")]
        mock_db_session.query.return_value.filter.return_value.all.return_value = routes
    
        response = self.app.get('/routes?status=Confirmada&type=Visita&assignee_id=0868a4ad-88ac-44e6-878d-5cd45a6f7703')
        
        self.assertEqual(response.status_code, 200)

    def test_get_routes_invalid_route_type(self):
        
        response = self.app.get('/routes?type=X')
        
        self.assertEqual(response.status_code, 400)
        
        self.assertEqual(response.data.decode(), '{"message": "invalid route type"}\n')

    def test_get_routes_invalid_route_status(self):
        
        response = self.app.get('/routes?status=X')
        
        self.assertEqual(response.status_code, 400)
        
        self.assertEqual(response.data.decode(), '{"message": "invalid route status"}\n')

    def test_get_routes_invalid_route_assignee(self):
        
        response = self.app.get('/routes?assignee_id=0868a4ad-88ac-44e6-878d-5cd45a6f770')
        
        self.assertEqual(response.status_code, 400)
        
        self.assertEqual(response.data.decode(), '{"message": "invalid assignee id"}\n')

