import unittest, os
from flask import Flask
from flask_restful import Api
from app import create_app 

class AppTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        self.app = create_app().test_client()
        self.app.testing = True 

    def test_ping_endpoint(self):
        response = self.app.get('/users/ping')
        
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(response.data.decode(), '"pong"\n')

if __name__ == '__main__':
    unittest.main()