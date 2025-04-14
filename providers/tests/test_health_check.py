import unittest
from flask import Flask
from flask_restful import Api
from views.health_check import HealthCheck 

class HealthCheckTestCase(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(HealthCheck, '/health')
        self.app = app.test_client()  
        self.app.testing = True 

    def test_health_check(self):
        response = self.app.get('/health')
        
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(response.data.decode(), '"pong"\n')