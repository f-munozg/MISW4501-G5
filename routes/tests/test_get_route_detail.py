import unittest, os
from flask import Flask
from flask_restful import Api
from views.get_route_detail import GetRouteDetail
from models.models import Route, RouteStop
from unittest.mock import patch, MagicMock

class GetRouteDetailTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(GetRouteDetail, '/routes/<route_id>')
        self.app = app.test_client()  
        self.app.testing = True 

    @patch("models.models.db.session")
    def test_get_route_detail(self, mock_db_session):
        route = Route(id="35eaa088-d14a-48b2-a744-276c8b10824c")
        routeStop = [RouteStop(), RouteStop()]
        mock_db_session.query.return_value.filter.return_value.first.return_value = route
        mock_db_session.query.return_value.filter.return_value.all.return_value = routeStop
        

        response = self.app.get('/routes/35eaa088-d14a-48b2-a744-276c8b10824c')
        
        self.assertEqual(response.status_code, 200)
        

    def test_get_route_detail_invalid_uuid(self):
        
        response = self.app.get('/routes/35eaa088-d14a-48b2-a744-276c8b10824')
        
        self.assertEqual(response.status_code, 400)
        
        self.assertEqual(response.data.decode(), '{"message": "invalid route id"}\n')

    @patch("models.models.db.session")
    def test_get_route_detail_route_not_found(self, mock_db_session):
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        response = self.app.get('/routes/35eaa088-d14a-48b2-a744-276c8b10824c')
        
        self.assertEqual(response.status_code, 404)
        
        self.assertEqual(response.data.decode(), '{"message": "route not found"}\n')