import unittest, os
from flask import Flask
from flask_restful import Api
from views.get_roles import GetRoles
from unittest.mock import patch, MagicMock

class GetRolesTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(GetRoles, '/users/roles')
        self.app = app.test_client()  
        self.app.testing = True 

    @patch("models.models.db.session")
    def test_get_roles(self, mock_db_session):
        mock_db_session.query = MagicMock()
        response = self.app.get('/users/roles')
        
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(response.data.decode(), '{"roles": []}\n')